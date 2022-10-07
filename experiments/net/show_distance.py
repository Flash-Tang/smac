#!/usr/bin/python

'This example creates a central network topology with 1 AP and 3 stations'

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
    "Create a star network topo."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    info("*** Adding access points\nap1\n")
    # ap1 = net.addAccessPoint('ap1', ssid="central_topo", mode="g",
    #                          channel="5", position='10,300,0')

    info("*** Adding stations\nsta1 sta2 sta3 sta4 sta5 sta6 sta7 sta8 sta9 sta10\n")

    pos = get_agent_pos()
    sta1 = net.addStation('sta1', position=pos[0])
    sta2 = net.addStation('sta2', position=pos[1])
    sta3 = net.addStation('sta3', position=pos[2])

    c0 = net.addController('c0')

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.plotGraph(max_x=500, max_y=500)

    info("*** Starting network\n")
    net.build()
    c0.start()


    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')

    env = StarCraft2Env(map_name="3m_distance")
    env_info = env.get_env_info()
    n_agents = env_info["n_agents"]
    env.reset()

    topology()