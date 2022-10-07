#!/usr/bin/python

'This example creates a grouped network topology with 3 AP and 10 stations'

import sys
sys.path.append('/home/alantang/PycharmProjects/MaRL_Env')

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi

from smac.env.starcraft2.starcraft2 import StarCraft2Env

SCALING = 20


def get_agent_pos():
    pos = []
    for agent_id in range(n_agents):
        unit = env.get_unit_by_id(agent_id)
        pos.append(str(int(unit.pos.x) * SCALING) + ',' + str(int(unit.pos.y) * SCALING) + ',' + '0')

    return pos


def topology():
    "Create a grouped network topo."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    info("*** Adding access points\nap1 ap2 ap3\n")
    ap1 = net.addAccessPoint('ap1', ssid="group1", mode="g",
                             channel="5", position='10,350,0')
    ap2 = net.addAccessPoint('ap2', ssid="group2", mode="g",
                             channel="5", position='10,200,0')
    ap3 = net.addAccessPoint('ap3', ssid="group3", mode="g",
                             channel="5", position='10,100,0')

    info("*** Adding stations\nsta1 sta2 sta3 sta4 sta5 sta6 sta7 sta8 sta9 sta10\n")
    pos = get_agent_pos()
    sta1 = net.addStation('sta1', position=pos[0])
    sta2 = net.addStation('sta2', position=pos[1])
    sta3 = net.addStation('sta3', position=pos[2])
    sta4 = net.addStation('sta4', position=pos[3])
    sta5 = net.addStation('sta5', position=pos[4])
    sta6 = net.addStation('sta6', position=pos[5])
    sta7 = net.addStation('sta7', position=pos[6])
    sta8 = net.addStation('sta8', position=pos[7])
    sta9 = net.addStation('sta9', position=pos[8])
    sta10 = net.addStation('sta10', position=pos[9])

    c0 = net.addController('c0')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Adding links:\n"
         "(sta1, ap1) (sta3, ap1) (sta4, ap1) "
         "(sta5, ap1) (sta6, ap1) (sta9, ap1) "
         "(sta10, ap1) (sta2, ap2) (sta8, ap2) "
         "(sta7, ap3)\n")
    net.addLink(sta1, ap1)
    net.addLink(sta3, ap1)
    net.addLink(sta4, ap1)
    net.addLink(sta5, ap1)
    net.addLink(sta6, ap1)
    net.addLink(sta9, ap1)
    net.addLink(sta10, ap1)
    net.addLink(sta2, ap2)
    net.addLink(sta8, ap2)
    net.addLink(sta7, ap3)

    net.plotGraph(max_x=500, max_y=500)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap1.start([c0])
    ap1.start([c0])

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

        ap1.cmd('ovs-ofctl add-flow ap3 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap3 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap3 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap3 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')


    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')

    env = StarCraft2Env(map_name="10m_grouped")
    env_info = env.get_env_info()
    n_agents = env_info["n_agents"]
    env.reset()

    topology()