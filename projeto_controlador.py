# ext/projeto_controlador.py
# Projeto SDN - Controlador POX e Rede Mininet
# Estudante: Matheus Johann Araujo

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.addresses import EthAddr, IPAddr
from pox.openflow.discovery import Discovery  
from pox.host_tracker import host_tracker
from host_tracker import launch as launch_host_tracker

class projeto_controlador(EventMixin):
    
    def __init__(self):
        launch_host_tracker()
        def startup():
            core.openflow.addListeners(self, priority = 0)
            core.openflow_discovery.addListeners(self)
            core.host_tracker.addListeners(self)
        core.call_when_ready(startup, ('openflow','openflow_discovery', 'host_tracker'))
        self.listenTo(core.openflow)

    def _handle_LinkEvent(self, event):
        print("-" * 160)
        link = event.link
        if event.added:
            print("Link Switches Added")            
        elif event.removed:
            print("Link Switches Removed")
        print("S{}-eth{}:S{}-eth{}".format(link.dpid1, link.port1, link.dpid2, link.port2))

    def _handle_HostEvent (self, event):
        print("-" * 160)
        print("Host: {} | Switch dpid: {} | Port: {}".format(EthAddr(event.entry.macaddr), event.entry.dpid, event.entry.port))

    # Variavel que armazena a conexao com os Switches
    switches = {}

    # DPIDs Switches
    dpid_S1 = None
    dpid_S2 = None
    dpid_S3 = None
    dpid_S4 = None
    dpid_S5 = None    

    def _handle_ConnectionUp(self, event) :
        print("-" * 160)
        print("Connection UP from Switch dpid: {}".format(event.dpid)) # Numero ID da conexao com o Switch
        self.switches[event.dpid] = event.connection # Conexao com o Switch            
        for m in event.connection.features.ports:            
            if m.port_no == 65534:
                continue
            print("Switch Eth: {} | Mac Port: {}".format(m.name, EthAddr(m.hw_addr)))
            if m.name == "S1-eth1":
                self.dpid_S1 = event.connection.dpid                
            elif m.name == "S2-eth1":
                self.dpid_S2 = event.connection.dpid                
            elif m.name == "S3-eth1":
                self.dpid_S3 = event.connection.dpid                
            elif m.name == "S4-eth1":
                self.dpid_S4 = event.connection.dpid                
            elif m.name == "S5-eth1":
                self.dpid_S5 = event.connection.dpid
        print("-" * 160)
        print("S1 dpid: {} | S2 dpid: {} | S3 dpid: {} | S4 dpid: {} | S5 dpid: {}".format(self.dpid_S1, self.dpid_S2, self.dpid_S3, self.dpid_S4, self.dpid_S5))

    def packet_type(self, packet):
        if packet.find('icmp'): return 'icmp'
        if packet.find('arp'):  return 'arp'
        if packet.find('dhcp'): return 'dhcp'
        if packet.find('tcp'):  return 'tcp'
        if packet.find('udp'):  return 'udp'
        if parsed.find('ipv4'): return "ipv4"
        return 'unknown'

    def flow_add(self, dpid, out_port = None, dl_type = None, priority = None, idle_timeout = None, hard_timeout = None, nw_src = None, nw_dst = None, in_port = None):
        msg = of.ofp_flow_mod()
        # PORT
        if out_port == None:
            out_port = [of.OFPP_ALL]
        elif isinstance(out_port, int):
            out_port = [out_port]
        if not isinstance(out_port, list):
            return
        # IPv4
        if isinstance(nw_src, str):
            nw_src = IPAddr(nw_src)
        if isinstance(nw_dst, str):
            nw_dst = IPAddr(nw_dst)
        print("-" * 160)
        print("SWITCH DPID: {} | IN_PORT: {} | OUT_PORT: {} | DL_TYPE: {} | PRIORITY: {} | IDLE_TIMEOUT: {} | HARD_TIMEOUT: {} | NW_SRC: {} | NW_DST: {}".format(dpid, in_port, out_port, dl_type, priority, idle_timeout, hard_timeout, nw_src, nw_dst))
        # priority
        if priority != None:
            msg.priority = priority
        # idle_timeout
        if idle_timeout != None:
            msg.idle_timeout = idle_timeout
        # hard_timeout
        if hard_timeout != None:
            msg.hard_timeout = hard_timeout
        # dl_type
        if dl_type != None:
            msg.match.dl_type = dl_type
        # nw_src
        if nw_src != None:
            msg.match.nw_src = nw_src
        # nw_dst
        if nw_dst != None:
            msg.match.nw_dst = nw_dst
        # in_port
        if in_port:
            msg.match.in_port = in_port
        for num in out_port:
            msg.actions.append(of.ofp_action_output(port = num))
        self.switches[dpid].send(msg)

    def flow_add_arp(self, dpid, out_port = None):
        self.flow_add(dpid, out_port=out_port, dl_type=0x0806, priority=1, idle_timeout=10, hard_timeout=10)

    def flow_add_ip(self, dpid, out_port = None, nw_src = None, nw_dst = None, in_port = None):
        self.flow_add(dpid, out_port=out_port, dl_type=0x0800, priority=10, idle_timeout=0, hard_timeout=0, nw_src=nw_src, nw_dst=nw_dst, in_port=in_port)

    def flow_add_in_port(self, dpid, out_port = None, nw_src = None, nw_dst = None, in_port = None):
        self.flow_add(dpid, out_port=out_port, priority=10, idle_timeout=0, hard_timeout=0, nw_src=nw_src, nw_dst=nw_dst, in_port=in_port)    

    def set_flow_S1(self, dpid):
        print("Set Flow S1")
        # S1-eth1:H1-eth0 S1-eth2:H2-eth0 S1-eth3:H3-eth0 S1-eth4:S2-eth1 S1-eth5:S3-eth1 S1-eth6:S4-eth1
        self.flow_add_arp(dpid)
        # S1-eth1:H1-eth0
        self.flow_add_ip(dpid, out_port = 1, nw_dst = "16.32.64.1")
        # S1-eth2:H2-eth0
        self.flow_add_ip(dpid, out_port = 2, nw_dst = "16.32.64.2")
        # S1-eth3:H3-eth0
        self.flow_add_ip(dpid, out_port = 3, nw_dst = "16.32.64.3")
        # S1-eth4:S2-eth1
        self.flow_add_ip(dpid, out_port = [4, 5], nw_dst = "16.32.64.4")
        # S1-eth5:S3-eth1
        self.flow_add_ip(dpid, out_port = 5, nw_dst = "16.32.64.5")
        # S1-eth6:S4-eth1
        self.flow_add_ip(dpid, out_port = [5, 6], nw_src = "16.32.64.3", nw_dst = "16.32.64.6")

    def set_flow_S2(self, dpid):
        print("Set Flow S2")
        # S2-eth1:S1-eth4 S2-eth3:H4-eth0
        self.flow_add_arp(dpid, out_port = [1, 3])        
        # S2-eth3:H4-eth0
        self.flow_add_ip(dpid, out_port = 3, nw_dst = "16.32.64.4")
        # S2-eth1:S1-eth4
        self.flow_add_in_port(dpid, out_port = 1, in_port = 3)
        # S2-eth2:S5-eth1
        self.flow_add_in_port(dpid, out_port = 3, in_port = 2)

    def set_flow_S3(self, dpid):
        print("Set Flow S3")
        # S3-eth1:S1-eth5 S3-eth2:S5-eth2
        self.flow_add_arp(dpid)
        # S3-eth2:S5-eth2
        self.flow_add_in_port(dpid, out_port = 2, in_port = 1)
        # S3-eth1:S1-eth5
        self.flow_add_in_port(dpid, out_port = 1, in_port = 2)

    def set_flow_S4(self, dpid):
        print("Set Flow S4")
        # S4-eth1:S1-eth6 S4-eth3:H6-eth0
        self.flow_add_arp(dpid, out_port = [1, 3])
        # S4-eth3:H6-eth0
        self.flow_add_ip(dpid, out_port = 3, nw_src = "16.32.64.3", nw_dst = "16.32.64.6")
        # S4-eth1:S1-eth6
        self.flow_add_in_port(dpid, out_port = 1, in_port = 3)

    def set_flow_S5(self, dpid):
        print("Set Flow S5")
        # S5-eth2:S3-eth2 S5-eth4:H5-eth0
        self.flow_add_arp(dpid, out_port = [2, 4])
        # S5-eth4:H5-eth0
        self.flow_add_ip(dpid, out_port = 4, nw_dst = "16.32.64.5", in_port = 2)
        # S5-eth2:S3-eth2
        self.flow_add_in_port(dpid, out_port = 2, in_port = 4)
        # S5-eth1:S2-eth2 S5-eth2:S3-eth2
        self.flow_add_ip(dpid, out_port = 1, nw_dst = "16.32.64.4", in_port = 2)
        # S5-eth3:S4-eth2 S5-eth2:S3-eth2
        self.flow_add_ip(dpid, out_port = 3, nw_dst = "16.32.64.6", in_port = 2)

    def set_flow(self, dpid):
        print("-" * 160)
        if dpid == self.dpid_S1:
            self.set_flow_S1(dpid)
        elif dpid == self.dpid_S2:
            self.set_flow_S2(dpid)
        elif dpid == self.dpid_S3:
            self.set_flow_S3(dpid)
        elif dpid == self.dpid_S4:
            self.set_flow_S4(dpid)
        elif dpid == self.dpid_S5:
            self.set_flow_S5(dpid)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        packet_type = self.packet_type(packet)
        print("-" * 160)
        print("PACKET TYPE: {} | SRC: {} | DST: {} | MULTICAST DST: {}".format(packet_type, EthAddr(packet.src), EthAddr(packet.dst), packet.dst.is_multicast))
        if packet_type == "unknown":
            return
        dpid = event.connection.dpid
        self.set_flow(dpid)

def launch():
    core.openflow.miss_send_len = 1024
    core.registerNew(projeto_controlador)
