import mininet.link

from smac.env import StarCraft2Env
import numpy as np
import os
from os import path
import time
import logging
from threading import Thread
import argparse
import matplotlib
import matplotlib.pyplot as plt

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg
from mininet.cli import CLI

lg.setLogLevel('info')
logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('-t', dest='topo', choices=['grouped', 'centered'], default='grouped')
parser.add_argument('-bw', dest='bandwidth', type=float, default=10.0)
args = parser.parse_args()
print(args)


def send_message(agent_id, agent_host, target_host):
    result = agent_host.cmd(f'python3 experiments/node_send.py -i {target_host.IP()} -d {agent_id}')
    logging.info(f'------------------agent{agent_id} status: {result}')


def agent2group(agent_id):
    if agent_id in range(2): return 0
    elif agent_id in range(2, 9): return 1
    else: return 2


def net_flow_cnt(message_dir='shared_buffer/message_to_sent'):
    size = 0
    for root, dirs, files in os.walk(message_dir):
        size += sum([path.getsize(path.join(root, name)) for name in files])
    return size / 1024


def draw_plot(centered_trans_times, hybrid_trans_times, centered_net_flow, hybrid_net_flow):
    # matplotlib.rcParams['font.sans-serif'] = ['Droid Sans Fallback']

    # ax = plt.subplot(2, 2, 1)
    plt.title('中心化模型传输时延', fontproperties='Droid Sans Fallback')
    plt.xlabel('游戏内步数', fontproperties='Droid Sans Fallback')
    plt.ylabel('传输时延（秒）', fontproperties='Droid Sans Fallback')
    plt.plot(list(range(100)), centered_trans_times, linewidth=5)
    plt.show()

    # ax = plt.subplot(2, 2, 2)
    plt.title('分层模型传输时延',  fontproperties='Droid Sans Fallback')
    plt.xlabel('游戏内步数', fontproperties='Droid Sans Fallback')
    plt.ylabel('传输时延（秒）', fontproperties='Droid Sans Fallback')
    plt.scatter([5 * i for i in range(20)], hybrid_trans_times, marker='+', color=['red'] * 20,
                label='control by leader')
    plt.scatter([i for i in range(100) if i % 5 != 0], [0] * 80, label='self control')
    plt.legend(loc='upper right')
    plt.show()

    # ax = plt.subplot(2, 2, 3)
    plt.title('两种模型网络流量对比', fontproperties='Droid Sans Fallback')
    plt.xlabel('模型', fontproperties='Droid Sans Fallback')
    plt.ylabel('网络流量', fontproperties='Droid Sans Fallback')
    plt.bar(['central model', 'multi-layer model'], [centered_net_flow, hybrid_net_flow], color=['red', 'green'], width=0.3)

    plt.show()


class CenteredMultiLinkTopo(Topo):
    """
    centered topology with multiple links
    """
    def __init__(self):
        Topo.__init__(self)
        self.receive_pros = []

    def build(self):
        # Switch
        self.addSwitch('s0')

        # Agent hosts
        for i in range(n_agents):
            a_host[i] = self.addHost('a{}'.format(i))
            self.addLink(a_host[i], 's0', bw=args.bandwidth, delay='20ms')

        # Central host
        c_host[0] = self.addHost('c0')
        self.addLink('c0', 's0', bw=args.bandwidth, delay='20ms')

    def receiver_set_up(self, net):
        for agent_id in range(n_agents):
            center_host = net.get(c_host[0])
            receive_pro = center_host.popen(
                f'python3 experiments/node_recv.py -i {center_host.IP()} -d {agent_id}')
            self.receive_pros.append(receive_pro)
        # Waiting receiver processed to set up
        time.sleep(3)

    def sender_send(self, net):
        threads = []
        for i in range(n_agents):
            agent_host = net.get(a_host[i])
            target_host = net.get(c_host[0])
            t = Thread(target=send_message, args=(i, agent_host, target_host))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


class GroupedMultiLinkTopo(Topo):
    """
    grouped topology with multiple links
    """
    def __init__(self):
        Topo.__init__(self)
        self.leader_hosts = []
        self.receive_pros = []
        self.group_start_stop_idxes = [(0, 2), (2, 9), (9, 10)]

    def build(self):
        # Switches
        for i in range(n_groups):
            switches[i] = self.addSwitch(f's{i}')

        # Agent hosts
        for i in range(n_agents):
            a_host[i] = self.addHost('a{}'.format(i))

            # Marauders
            if i < 2:
                self.addLink(a_host[i], switches[0], bw=args.bandwidth, delay='20ms')

            # Marines
            elif i < 9:
                self.addLink(a_host[i], switches[1], bw=args.bandwidth, delay='20ms')

            # Medivac
            else:
                self.addLink(a_host[i], switches[2], bw=args.bandwidth, delay='20ms')

        # Leader hosts
        for i in range(n_groups):
            l_host[i] = self.addHost('l{}'.format(i))
            self.addLink(l_host[i], switches[i], bw=args.bandwidth, delay='20ms')

    def receiver_set_up(self, net):
        for i in range(n_groups):
            leader_host = net.get(l_host[i])
            self.leader_hosts.append(leader_host)

        for agent_id in range(n_agents):
            agent_group = agent2group(agent_id)
            receive_pro = self.leader_hosts[agent_group].popen(
                f'python3 experiments/node_recv.py -i {self.leader_hosts[agent_group].IP()} -d {agent_id}')
            self.receive_pros.append(receive_pro)
        # Waiting receiver processed to set up
        time.sleep(3)

    def sender_send(self, net):
        threads = []
        for i in range(n_agents):
            agent_host = net.get(a_host[i])
            target_host = net.get(l_host[agent2group(i)])
            t = Thread(target=send_message, args=(i, agent_host, target_host))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


def main():
    # Centered Topo
    topo = CenteredMultiLinkTopo()
    net = Mininet(topo=topo, link=mininet.link.TCLink)
    net.start()
    CLI(net)
    topo.receiver_set_up(net)


    n_episode = 1
    n_step = 201

    for e in range(n_episode):
        env.reset()
        centered_trans_times, hybrid_trans_times = [], []
        centered_net_flow, hybrid_net_flow = 0, 0

        for step in range(n_step):
            obs, _ = env.get_obs()

            # Agent saves obs of their own
            for agent_id, agent_obs in enumerate(obs):
                logging.info(f'agent{agent_id}\'s obs shape: {agent_obs.shape}')
                np.save(f'shared_buffer/message_to_sent/agent_{agent_id}_obs', obs[agent_id])

            # Centered mode
            if step < 100:
                start_time = time.time()
                topo.sender_send(net)
                trans_time = np.round(time.time() - start_time, 3)
                centered_trans_times.append(trans_time)
                centered_net_flow += net_flow_cnt()
                print(f'one pass time(centered mode): {trans_time}')
                for receiver in topo.receive_pros:
                    logging.info(f'---------------------receiver status: {receiver.stdout.readlines()}')
            elif step == 100:
                for rp in topo.receive_pros:
                    rp.terminate()
                CLI(net)
                # Switch to Grouped Topo
                net.stop()
                topo = GroupedMultiLinkTopo()
                net = Mininet(topo=topo)
                net.start()
                topo.receiver_set_up(net)
                # CLI(net)
            # Hybrid mode
            else:
                if step % 5 == 0:
                    start_time = time.time()
                    topo.sender_send(net)
                    trans_time = np.round(time.time() - start_time, 3)
                    hybrid_trans_times.append(trans_time)
                    hybrid_net_flow += net_flow_cnt()
                    print(f'one pass time(Hybrid mode): {trans_time}')
                    for receiver in topo.receive_pros:
                        logging.info(f'---------------------receiver status: {receiver.stdout.readlines()}')

            print('---------------------------------step------------------------------------')

    for rp in topo.receive_pros:
        rp.terminate()
    net.stop()
    env.close()

    draw_plot(centered_trans_times, hybrid_trans_times, centered_net_flow, hybrid_net_flow)


if __name__ == "__main__":
    env = StarCraft2Env(map_name="MMM", debug=False)

    env_info = env.get_env_info()
    n_actions = env_info["n_actions"]
    n_agents = env_info["n_agents"]
    n_groups = 3
    # Agent host
    a_host = [''] * n_agents
    # Leader host for grouped topo
    l_host = [''] * n_groups
    # Central host for centered topo
    c_host = ['']
    switches = [''] * n_groups

    main()
