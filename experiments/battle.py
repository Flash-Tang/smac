from smac.env import StarCraft2Env

import maddpg.common.tf_util as U
import tensorflow as tf
import numpy as np
from algos.algo_util import get_actors, get_actions, get_leader_actors

from train_group_leader import p2a


def main():
    env = StarCraft2Env(map_name="MMM", policy_agents_num=2)
    env_info = env.get_env_info()
    n_agents = env_info["n_agents"]
    n_groups = 3

    n_episodes = 20
    win_cnt = 0

    g1 = tf.Graph()
    g2 = tf.Graph()

    sess1 = tf.Session(graph=g1)
    sess2 = tf.Session(graph=g2)

    with sess1.as_default():
        with g1.as_default():
            blue_leaders = get_leader_actors(env, n_groups)
            U.initialize()
            U.load_state('/tmp/policy/0.03')

    with sess2.as_default():
        with g2.as_default():
            red_actors = get_actors(env, n_agents)
            blue_actors = get_actors(env, n_agents)

            U.initialize()
            U.load_state('./policy/agents_policy/0.31')

    for e in range(n_episodes):
        env.reset()
        terminal = False
        ep_step = 0

        while not terminal:
            if False:
                with sess1.as_default():
                    with g1.as_default():
                        obs_n = env.get_obs_leader_n(side='blue')
                        policy_vec_n = [leader.action(obs) for leader, obs in zip(blue_leaders, obs_n)]
                        policy_int_n = [np.argmax(policy_vec) for policy_vec in policy_vec_n]
                        # get action
                        blue_act = p2a(policy_int_n, env, side='blue')

                with sess2.as_default():
                    with g2.as_default():
                        red_obs, _ = env.get_obs()
                        red_act = get_actions(red_actors, red_obs, env, 'red')

            else:
                with sess2.as_default():
                    with g2.as_default():
                        red_obs, blue_obs = env.get_obs()

                        red_act = get_actions(red_actors, red_obs, env, 'red')
                        blue_act = get_actions(blue_actors, blue_obs, env, 'blue')

            # environment step
            _, terminal, info = env.step([red_act, blue_act])
            ep_step += 1

        if info['battle_won']:
            print(f'win game {e}')
            win_cnt += 1
        else:
            print(f'lose game {e}')
        env.close()

    env.close()
    print('win rate {}'.format(1 - (win_cnt / n_episodes)))


if __name__ == "__main__":
    main()
