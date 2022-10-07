#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi


def topology():
    "Create a network."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    sta_arg = dict()
    ap_arg = dict()
    if '-v' in sys.argv:
        sta_arg = {'nvif': 2}
    else:
        # isolate_clientes: Client isolation can be used to prevent low-level
        # bridging of frames between associated stations in the BSS.
        # By default, this bridging is allowed.
        # OpenFlow rules are required to allow communication among nodes
        ap_arg = {'client_isolation': True}

    info("*** Adding access points\n")
    ap1 = net.addAccessPoint('ap1', ssid="simpletopo1", mode="g",
                             channel="5", **ap_arg)
    ap2 = net.addAccessPoint('ap2', ssid="simpletopo2", mode="g",
                             channel="5", **ap_arg)

    info("*** Adding stations\n")
    sta1 = net.addStation('sta1', **sta_arg)
    sta2 = net.addStation('sta2')
    sta3 = net.addStation('sta3')
    sta4 = net.addStation('sta4')
    sta5 = net.addStation('sta5')
    sta6 = net.addStation('sta6')
    sta7 = net.addStation('sta7')
    sta8 = net.addStation('sta8')
    sta9 = net.addStation('sta9')
    sta10 = net.addStation('sta10')

    c0 = net.addController('c0')
    c1 = net.addController('c1')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap1)
    net.addLink(sta4, ap1)
    net.addLink(sta5, ap1)
    net.addLink(sta6, ap1)
    net.addLink(sta7, ap1)
    net.addLink(sta8, ap2)
    net.addLink(sta9, ap2)
    net.addLink(sta10, ap2)

    info("*** Starting network\n")
    net.build()
    c0.start()
    c1.start()
    ap1.start([c0])
    ap2.start([c1])

    if '-v' not in sys.argv:
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

        ap2.cmd('ovs-ofctl add-flow ap2 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap2.cmd('ovs-ofctl add-flow ap2 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap2.cmd('ovs-ofctl add-flow ap2 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap2.cmd('ovs-ofctl add-flow ap2 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()