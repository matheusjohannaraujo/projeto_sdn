#!/usr/bin/python
# Projeto SDN - Controlador POX e Rede Mininet
# Estudante: Matheus Johann Araujo

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='16.32.64.0/8')

    info( '*** Adding controller\n' )
    C0=net.addController(name='C0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    S1 = net.addSwitch('S1', cls=OVSKernelSwitch, dpid='1')
    S2 = net.addSwitch('S2', cls=OVSKernelSwitch, dpid='2')
    S3 = net.addSwitch('S3', cls=OVSKernelSwitch, dpid='3')    
    S4 = net.addSwitch('S4', cls=OVSKernelSwitch, dpid='4')
    S5 = net.addSwitch('S5', cls=OVSKernelSwitch, dpid='5')

    info( '*** Add hosts\n')
    H1 = net.addHost('H1', cls=Host, ip='16.32.64.1', mac='a0:00:00:00:00:01', defaultRoute=None)
    H2 = net.addHost('H2', cls=Host, ip='16.32.64.2', mac='a0:00:00:00:00:02', defaultRoute=None)
    H3 = net.addHost('H3', cls=Host, ip='16.32.64.3', mac='a0:00:00:00:00:03', defaultRoute=None)
    H4 = net.addHost('H4', cls=Host, ip='16.32.64.4', mac='b0:00:00:00:00:04', defaultRoute=None)
    H5 = net.addHost('H5', cls=Host, ip='16.32.64.5', mac='c0:00:00:00:00:05', defaultRoute=None)
    H6 = net.addHost('H6', cls=Host, ip='16.32.64.6', mac='d0:00:00:00:00:06', defaultRoute=None)

    info( '*** Add links\n')

    #S1H1 = S1H2 = S1H3 = S2H4 = S5H5 = S4H6 = {'bw':100,'max_queue_size':100}
    #S1S2 = S1S3 = S1S4 = S2S5 = S3S5 = S4S5 = {'bw':100,'max_queue_size':100}

    S1H1 = S1H2 = S1H3 = S2H4 = S5H5 = S4H6 = {'bw':100,'max_queue_size':100,'loss':1}
    S1S2 = S1S3 = S1S4 = S2S5 = S3S5 = S4S5 = {'bw':100,'max_queue_size':100,'loss':2,'delay':'1ms'}

    net.addLink(S1, H1, cls=TCLink , **S1H1)
    net.addLink(S1, H2, cls=TCLink , **S1H2)
    net.addLink(S1, H3, cls=TCLink , **S1H3)
    net.addLink(S1, S2, cls=TCLink , **S1S2)
    net.addLink(S1, S3, cls=TCLink , **S1S3)
    net.addLink(S1, S4, cls=TCLink , **S1S4)
    net.addLink(S2, S5, cls=TCLink , **S2S5)    
    net.addLink(S2, H4, cls=TCLink , **S2H4)
    net.addLink(S3, S5, cls=TCLink , **S3S5)    
    net.addLink(S4, S5, cls=TCLink , **S4S5)
    net.addLink(S5, H5, cls=TCLink , **S5H5)    
    net.addLink(S4, H6, cls=TCLink , **S4H6)    

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    
    net.get('S1').start([C0])
    net.get('S2').start([C0])
    net.get('S3').start([C0])
    net.get('S5').start([C0])    
    net.get('S4').start([C0])

    info( '*** Post configure switches and hosts\n')
    
    net.start()

    info( '*** Testing network\n')
    
    cmd_ping = "ping -c 1"

    print("")
    print("H1 {} H2".format(cmd_ping))
    print H1.cmd(cmd_ping, H2.IP())

    print("")
    print("H2 {} H3".format(cmd_ping))
    print H2.cmd(cmd_ping, H3.IP())

    print("")
    print("H3 {} H4".format(cmd_ping))
    print H3.cmd(cmd_ping, H4.IP())

    print("")
    print("H1 {} H5".format(cmd_ping))
    print H1.cmd(cmd_ping, H5.IP())

    print("")
    print("H3 {} H6".format(cmd_ping))
    print H3.cmd(cmd_ping, H6.IP())

    print("")
    print("pingall")
    net.pingAll()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
