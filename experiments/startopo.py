import mininet.link

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg
from mininet.cli import CLI

lg.setLogLevel('info')
# logging.basicConfig(level=logging.ERROR)


class StarTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

    def build(self):
        # Switch
        # self.addSwitch('s0')

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        self.addLink('h1', 'h2')
        self.addLink('h1', 'h3')


def main():
    topo = StarTopo()
    net = Mininet(topo=topo, link=mininet.link.TCLink)
    net.start()
    CLI(net)

    net.stop()


if __name__ == "__main__":
    main()

