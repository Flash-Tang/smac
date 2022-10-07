import mininet.link

from smac.env import StarCraft2Env
import os
from os import path
import logging
import argparse

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg
from mininet.cli import CLI

lg.setLogLevel('info')
logging.basicConfig(level=logging.ERROR)


parser = argparse.ArgumentParser()
parser.add_argument('-t', dest='topo', choices=['centered', 'decentralized', 'hybrid'], default='grouped')
parser.add_argument('-bw', dest='bandwidth', type=float, default=10.0)
args = parser.parse_args()
print(args)

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


class DecentralizedMultiLinkTopo(Topo):
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


class HybridMultiLinkTopo(Topo):
    """
    hybrid topology with multiple links
    """
    def __init__(self):
        Topo.__init__(self)
        self.receive_pros = []

    def build(self):
        # Switch
        self.addSwitch('s0')
        self.addSwitch('s1')

        # Grouped hosts
        for i in range(5):
            a_host[i] = self.addHost('ga{}'.format(i))
            self.addLink(a_host[i], 's0', bw=args.bandwidth, delay='20ms')

        # Group's leader host
        l_host[0] = self.addHost('l0')
        self.addLink('l0', 's0', bw=args.bandwidth, delay='20ms')

        # Indie hosts
        for i in range(5, 10):
            a_host[i] = self.addHost('ia{}'.format(i))
            self.addLink(a_host[i], 's1', bw=args.bandwidth, delay='20ms')


def main():
    if args.topo == 'centered':
        topo = CenteredMultiLinkTopo()
    elif args.topo == 'decentralized':
        topo = DecentralizedMultiLinkTopo()
    elif args.topo == 'hybrid':
        topo = HybridMultiLinkTopo()

    net = Mininet(topo=topo, link=mininet.link.TCLink)
    net.start()

    CLI(net)

    net.stop()
    env.close()


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
