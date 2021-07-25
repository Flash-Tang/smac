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

    n_episodes = 100
    win_cnt = 0

    g1 = tf.Graph()
    g2 = tf.Graph()

    leaders_sess = tf.Session(graph=g1)
    agents_sess = tf.Session(graph=g2)

    with leaders_sess.as_default():
        with g1.as_default():
            leaders = get_leader_actors(env, n_groups)
            U.initialize()
            U.load_state('./policy/leaders_policy/')

    with agents_sess.as_default():
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
            with agents_sess.as_default():
                with g2.as_default():
                    red_obs, blue_obs = env.get_obs()

                    red_act = get_actions(red_actors, red_obs, env, 'red')
                    blue_act = get_actions(blue_actors, blue_obs, env, 'blue')

            if ep_step % 2 == 0:
                with leaders_sess.as_default():
                    with g1.as_default():
                        obs_n = env.get_obs_leader_n(side='red')
                        policy_vec_n = [leader.action(obs) for leader, obs in zip(leaders, obs_n)]
                        policy_int_n = [np.argmax(policy_vec) for policy_vec in policy_vec_n]
                        # get action
                        red_act = p2a(policy_int_n, env, side='red')

            # environment step
            _, terminal, info = env.step([red_act, blue_act])
            ep_step += 1

        # TODO(alan): Now if time runs up, red_side lose regardless of how many agent left?
        if info['battle_won']:
            print('win game {}'.format(e))
            win_cnt += 1
        else:
            print('lose game {}'.format(e))
        env.close()
        print('current win rate {}'.format(win_cnt / (e + 1)))

    print('win rate {}'.format(win_cnt / n_episodes))


if __name__ == "__main__":
    main()
