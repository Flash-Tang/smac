import argparse
import numpy as np
import tensorflow as tf
import time
from gym import spaces

import maddpg.common.tf_util as U
from maddpg.trainer.maddpg import MADDPGAgentTrainer
import tensorflow.contrib.layers as layers

from smac.env import StarCraft2Env


def parse_args():
    parser = argparse.ArgumentParser("Reinforcement Learning experiments for multiagent environments")
    # Environment
    # TODO(alan): change to pass from smac_maps's config
    parser.add_argument("--max-episode-len", type=int, default=150, help="maximum episode length")
    parser.add_argument("--num-episodes", type=int, default=60000, help="number of episodes")
    parser.add_argument("--num-adversaries", type=int, default=0, help="number of adversaries")
    parser.add_argument("--good-policy", type=str, default="maddpg", help="policy for good agents")
    parser.add_argument("--adv-policy", type=str, default="maddpg", help="policy of adversaries")
    # Core training parameters
    parser.add_argument("--lr", type=float, default=1e-2, help="learning rate for Adam optimizer")
    parser.add_argument("--gamma", type=float, default=0.95, help="discount factor")
    parser.add_argument("--batch-size", type=int, default=1024, help="number of episodes to optimize at the same time")
    parser.add_argument("--num-units", type=int, default=64, help="number of units in the mlp")
    # Checkpointing
    parser.add_argument("--exp-name", type=str, default='maddpg_in_smac', help="name of the experiment")
    parser.add_argument("--save-dir", type=str, default="/tmp/policy/", help="directory in which training state and model should be saved")
    parser.add_argument("--save-rate", type=int, default=100, help="save model once every time this many episodes are completed")
    parser.add_argument("--load-dir", type=str, default="", help="directory in which training state and model are loaded")
    # Evaluation
    parser.add_argument("--restore", action="store_true", default=False)
    parser.add_argument("--display", action="store_true", default=False)
    parser.add_argument("--benchmark", action="store_true", default=False)
    parser.add_argument("--benchmark-iters", type=int, default=100000, help="number of iterations run for benchmarking")
    parser.add_argument("--benchmark-dir", type=str, default="./benchmark_files/", help="directory where benchmark data is saved")
    parser.add_argument("--plots-dir", type=str, default="./learning_curves/", help="directory where plot data is saved")
    return parser.parse_args()


POLICY_NUM = 3

def mlp_model(input, num_outputs, scope, reuse=False, num_units=64, rnn_cell=None):
    # This model takes as input an observation and returns values of all actions
    with tf.variable_scope(scope, reuse=reuse):
        out = input
        out = layers.fully_connected(out, num_outputs=num_units, activation_fn=tf.nn.relu)
        out = layers.fully_connected(out, num_outputs=num_units, activation_fn=tf.nn.relu)
        out = layers.fully_connected(out, num_outputs=num_outputs, activation_fn=None)
        return out


def get_trainers(env, n_groups, obs_shape_n, arglist):
    trainers = []
    model = mlp_model
    trainer = MADDPGAgentTrainer
    for i in range(n_groups):
        trainers.append(trainer(
            "leader_%d" % i, model, obs_shape_n, [spaces.Discrete(POLICY_NUM) for _ in range(n_groups)], i, arglist,
        ))
    return trainers


def p2a(policy_int_n, env):
    n_actions = [-1] * env.n_agents
    # Redundant
    en_health = np.zeros((env.n_agents, ), dtype=np.float32)
    en_id = np.zeros((env.n_agents, 3), dtype=np.float32)

    for agent_id in range(env.n_agents):
        agent_obs = env.get_enemy_obs_agent(agent_id, en_health, en_id).reshape(env.n_agents, 6)
        if agent_id in range(2):
            policy = policy_int_n[0]
        elif agent_id in range(2, 9):
            policy = policy_int_n[1]
        else:
            policy = policy_int_n[2]

        # Distance first policy
        if policy == 0:
            target_en = np.argmin(agent_obs[:, 1])
        # Health first policy
        elif policy == 1:
            target_en = np.argmin(agent_obs[:, 2])
        # Type first policy
        elif policy == 2:
            if np.any(agent_obs[:, -1]):
                target_en = np.nonzero(agent_obs[:, -1])[0][-1]
            elif np.any(agent_obs[:, -2]):
                target_en = np.nonzero(agent_obs[:, -2])[0][-1]
            elif np.any(agent_obs[:, -3]):
                target_en = np.nonzero(agent_obs[:, -3])[0][-1]
            # TODO(alan): TBD
            else:
                target_en = 4

        act = env.n_actions_no_attack + target_en
        avail_actions = env.get_avail_agent_actions(agent_id)
        if avail_actions[act] == 1:
            n_actions[agent_id] = act
        # TODO(alan): TBD
        else:
            n_actions[agent_id] = np.nonzero(avail_actions)[0][-1]

    return n_actions


def train(arglist):
    # TODO(alan) : Set multi-cpu to boost training
    with U.multi_threaded_session():
        # Create environment
        env = StarCraft2Env(map_name="MMM", difficulty='5')
        env_info = env.get_env_info()

        n_agents = env_info["n_agents"]
        n_groups = 3

        # Create agent trainers
        obs_shape_n = [(60,) for _ in range(n_groups)]
        trainers = get_trainers(env, n_groups, obs_shape_n, arglist)

        # Initialize
        U.initialize()

        # Load previous results, if necessary
        if arglist.load_dir == "":
            arglist.load_dir = arglist.save_dir
        if arglist.display or arglist.restore or arglist.benchmark:
            print('Loading previous state...')
            U.load_state(arglist.load_dir)

        episode_rewards = [0.0]  # sum of rewards for all agents
        episode_win = []
        episode_killing = []
        episode_remaining = []
        group_rewards = [[0.0] for _ in range(n_groups)]  # individual agent reward
        agent_info = [[[]]]  # placeholder for benchmarking info
        saver = tf.train.Saver()
        env.reset()
        episode_step = 0
        train_step = 0
        t_start = time.time()

        print('Starting iterations...')
        while True:
            obs_n = env.get_obs_leader_n()
            policy_vec_n = [leader.action(obs) for leader, obs in zip(trainers, obs_n)]
            policy_int_n = [np.argmax(policy_vec) for policy_vec in policy_vec_n]
            # get action
            actions_n = p2a(policy_int_n, env)

            # environment step
            rew_n, terminal, info = env.step([actions_n])
            rew_n = list(rew_n)
            rew_n = [sum(rew_n[:2]), sum(rew_n[2:9]), sum(rew_n[9:10])]
            # TODO(alan): set individual reward
            new_obs_n = env.get_obs_leader_n()
            done_n = [False for _ in range(n_groups)]
            episode_step += 1
            done = all(done_n)
            # collect experience
            for i, leader in enumerate(trainers):
                leader.experience(obs_n[i], policy_vec_n[i], rew_n[i], new_obs_n[i], done_n[i], terminal)

            for i, rew in enumerate(rew_n):
                episode_rewards[-1] += rew
                group_rewards[i][-1] += rew

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
                for a in group_rewards:
                    a.append(0)
                agent_info.append([[]])

            # increment global step counter
            train_step += 1

            # update all trainers, if not in display or benchmark mode
            loss = None
            for agent in trainers:
                agent.preupdate()
            for agent in trainers:
                loss = agent.update(trainers, train_step)

            # save model, display training output
            if terminal and (len(episode_rewards) % arglist.save_rate == 0):
                latest_won_rate = round(np.mean(episode_win[-arglist.save_rate:]), 2)
                U.save_state(arglist.save_dir, latest_won_rate, saver)
                print("steps: {}, episodes: {}, mean won rate: {}, mean episode reward: {}, agent episode reward: {}, "
                      "mean episode killing: {}, mean_epsode remaining: {}, time: {}"
                      .format(
                        train_step,
                        len(episode_rewards),
                        latest_won_rate,
                        round(np.mean(episode_rewards[-arglist.save_rate:]), 1),
                        [round(np.mean(rew[-arglist.save_rate:]), 1) for rew in group_rewards],
                        round(np.mean(episode_killing[-arglist.save_rate:]), 2),
                        round(np.mean(episode_remaining[-arglist.save_rate:]), 2),
                        round(time.time()-t_start, 2)
                            )
                    )

                env.save_replay(latest_won_rate)

                t_start = time.time()

            if len(episode_rewards) > arglist.num_episodes:
                break
    env.close()


if __name__ == '__main__':
    arglist = parse_args()
    train(arglist)
