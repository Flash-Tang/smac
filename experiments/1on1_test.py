from smac.env import StarCraft2Env
import numpy as np


def main():
    env = StarCraft2Env(map_name="3m", policy_agents_num=2)
    env_info = env.get_env_info()

    n_agents = env_info["n_agents"]

    n_episodes = 10

    for e in range(n_episodes):
        env.reset()
        terminated = False
        episode_reward = 0

        while not terminated:
            red_obs, blue_obs = env.get_obs()
            state = env.get_state()

            red_act, blue_act = [], []
            act_both_sides = []
            for agent_id in range(n_agents):
                avail_actions = env.get_avail_agent_actions(agent_id, side='red')
                avail_actions_ind = np.nonzero(avail_actions)[0]
                action = np.random.choice(avail_actions_ind)
                red_act.append(action)

            for agent_id in range(n_agents):
                avail_actions = env.get_avail_agent_actions(agent_id, side='blue')
                avail_actions_ind = np.nonzero(avail_actions)[0]
                action = np.random.choice(avail_actions_ind)
                blue_act.append(action)
            act_both_sides.append(red_act)
            act_both_sides.append(blue_act)

            reward, terminated, _ = env.step(act_both_sides)
            episode_reward += reward

        print("Total reward in episode {} = {}".format(e, episode_reward))

    env.close()


if __name__ == "__main__":
    main()
