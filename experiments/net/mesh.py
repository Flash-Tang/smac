#!/usr/bin/python

"""
This example shows on how to enable the mesh mode
The wireless mesh network is based on IEEE 802.11s
"""

import sys
sys.path.append('/home/alantang/PycharmProjects/MaRL_Env')

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, mesh
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

from smac.env.starcraft2.starcraft2 import StarCraft2Env

SCALING = 20


def get_agent_pos():
    pos = []
    for agent_id in range(n_agents):
        unit = env.get_unit_by_id(agent_id)
        pos.append(str(int(unit.pos.x) * SCALING) + ',' + str(int(unit.pos.y) * SCALING) + ',' + '0')

    return pos



def topology():
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
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

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(sta1, cls=mesh, ssid='meshNet',
                intf='sta1-wlan0', channel=5, ht_cap='HT40+')  #, passwd='thisisreallysecret')
    net.addLink(sta2, cls=mesh, ssid='meshNet',
                intf='sta2-wlan0', channel=5, ht_cap='HT40+')  #, passwd='thisisreallysecret')
    net.addLink(sta3, cls=mesh, ssid='meshNet',
                intf='sta3-wlan0', channel=5, ht_cap='HT40+')  #, passwd='thisisreallysecret')
    net.addLink(sta4, cls=mesh, ssid='meshNet',
                intf='sta4-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta5, cls=mesh, ssid='meshNet',
                intf='sta5-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta6, cls=mesh, ssid='meshNet',
                intf='sta6-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta7, cls=mesh, ssid='meshNet',
                intf='sta7-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta8, cls=mesh, ssid='meshNet',
                intf='sta8-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta9, cls=mesh, ssid='meshNet',
                intf='sta9-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')
    net.addLink(sta10, cls=mesh, ssid='meshNet',
                intf='sta10-wlan0', channel=5, ht_cap='HT40+')  # , passwd='thisisreallysecret')

    net.plotGraph(max_x=500, max_y=500)

    info("*** Starting network\n")
    net.build()

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')

    env = StarCraft2Env(map_name="10m_mesh")
    env_info = env.get_env_info()
    n_agents = env_info["n_agents"]
    env.reset()

    topology()