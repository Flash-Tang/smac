import argparse
import numpy as np
import tensorflow as tf
import time

import maddpg.common.tf_util as U
from maddpg.trainer.maddpg import MADDPGAgentActor
import tensorflow.contrib.layers as layers

from smac.env import StarCraft2Env


def mlp_model(input, num_outputs, scope, reuse=False, num_units=64, rnn_cell=None):
    # This model takes as input an observation and returns values of all actions
    with tf.variable_scope(scope, reuse=reuse):
        out = input
        out = layers.fully_connected(out, num_outputs=num_units, activation_fn=tf.nn.relu)
        out = layers.fully_connected(out, num_outputs=num_units, activation_fn=tf.nn.relu)
        out = layers.fully_connected(out, num_outputs=num_outputs, activation_fn=None)
        return out


def get_actors(env, n_agents, obs_shape_n):
    actors = []
    model = mlp_model
    actor = MADDPGAgentActor
    for i in range(n_agents):
        actors.append(actor(
            "agent_%d" % i, model, obs_shape_n, env.action_space(), i))
    return actors


def main():
    with U.single_threaded_session():
        env = StarCraft2Env(map_name="MMM")
        env_info = env.get_env_info()
        n_agents = env_info['n_agents']
        obs_shape_n = [(env.get_obs_size(),) for _ in range(n_agents)]
        actors_both_sides = []
        for _ in range(1):
            actors_both_sides.append(get_actors(env, n_agents, obs_shape_n))

        U.initialize()
        U.load_state('./policy/agents_policy/0.31')

        episode_rewards = [0.0]  # sum of rewards for all agents
        episode_win = []
        episode_killing = []
        episode_remaining = []
        agent_rewards = [[0.0] for _ in range(n_agents)]  # individual agent reward
        agent_info = [[[]]]  # placeholder for benchmarking info
        env.reset()
        episode_step = 0
        train_step = 0
        save_rate = 100
        t_start = time.time()

        print('Starting interaction...')
        while True:
            red_obs_n, _ = env.get_obs()
            # get action
            action_n = [agent.action(obs) for agent, obs in zip(actors_both_sides[0], red_obs_n)]
            action_for_smac = [np.argmax(action_ar) for action_ar in action_n]
            action_for_smac = [action if env.get_avail_agent_actions(agent)[action] else
                               np.nonzero(env.get_avail_agent_actions(agent))[0][-1] for agent, action in
                               enumerate(action_for_smac)]
            action_for_smac = [action if env.is_agent_alive(agent) else 0 for agent, action in
                               enumerate(action_for_smac)]
            # environment step
            rew_n, terminal, info = env.step([action_for_smac])
            rew_n = list(rew_n)
            done_n = [False for _ in range(n_agents)]
            episode_step += 1
            done = all(done_n)

            for i, rew in enumerate(rew_n):
                episode_rewards[-1] += rew
                agent_rewards[i][-1] += rew

            if done or terminal:
                game_restart = not ('dead_enemies' in info.keys())
                enemy_killed_num = info.get('dead_enemies', 0)
                self_left_num = n_agents - info.get('dead_allies', 0)
                if not game_restart:
                    episode_killing.append(enemy_killed_num)
                    episode_remaining.append(self_left_num)
                    episode_win.append(1 if info['battle_won'] else 0)
                env.reset()
                episode_step = 0
                episode_rewards.append(0)
                for a in agent_rewards:
                    a.append(0)
                agent_info.append([[]])

            # increment global step counter
            train_step += 1

            if terminal and len(episode_rewards) % save_rate == 0:
                print(
                    "steps: {}, episodes: {}, mean won rate: {}, mean episode reward: {}, agent episode reward: {}, mean episode killing: {}, mean_epsode remaining: {}, time: {}".format(
                        train_step, len(episode_rewards),
                        round(np.mean(episode_win[-save_rate:]), 2),
                        round(np.mean(episode_rewards[-save_rate:]), 1),
                        [round(np.mean(rew[-save_rate:]), 1) for rew in agent_rewards],
                        round(np.mean(episode_killing[-save_rate:]), 2),
                        round(np.mean(episode_remaining[-save_rate:]), 2),
                        round(time.time() - t_start, 2)))

                env.save_replay(round(np.mean(episode_win[-save_rate:]), 2))

                t_start = time.time()

    env.close()


if __name__ == '__main__':
    main()
