from smac.env import StarCraft2Env

import maddpg.common.tf_util as U
from algos.algo_util import get_actors, get_actions


def main():
    env = StarCraft2Env(map_name="MMM", policy_agents_num=2)
    env_info = env.get_env_info()
    n_agents = env_info["n_agents"]

    n_episodes = 100
    win_cnt = 0

    with U.single_threaded_session():

        red_actors = get_actors(env, n_agents)
        blue_actors = get_actors(env, n_agents)

        U.initialize()
        U.load_state('./policy/agents_policy/0.31')
        for e in range(n_episodes):
            env.reset()
            terminal = False

            while not terminal:
                red_obs, blue_obs = env.get_obs()

                red_act = get_actions(red_actors, red_obs, env, 'red')
                blue_act = get_actions(blue_actors, blue_obs, env, 'blue')

                # environment step
                _, terminal, info = env.step([red_act, blue_act])

            if info['battle_won']:
                print(f'win game {e}')
                win_cnt += 1
            else:
                print(f'lose game {e}')

    env.close()
    print('win rate {.2f}'.format(win_cnt / n_episodes))


if __name__ == "__main__":
    main()
