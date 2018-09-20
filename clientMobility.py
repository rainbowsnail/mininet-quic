#!/usr/bin/python

"""
Simple example of Mobility with Mininet
(aka enough rope to hang yourself.)
We move a host from s1 to s2, s2 to s3, and then back to s1.
Gotchas:
The reference controller doesn't support mobility, so we need to
manually flush the switch flow tables!
Good luck!
to-do:
- think about wifi/hub behavior
- think about clearing last hop - why doesn't that work?
"""

import time 
from mininet.net import Mininet
from mininet.node import OVSSwitch
#from mininet.topo import LinearTopo
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.log import info, output, warn, setLogLevel
from mininet.util import irange

from random import randint


class MobilitySwitch( OVSSwitch ):
    "Switch that can reattach and rename interfaces"

    def delIntf( self, intf ):
        "Remove (and detach) an interface"
        port = self.ports[ intf ]
        del self.ports[ intf ]
        del self.intfs[ port ]
        del self.nameToIntf[ intf.name ]

    def addIntf( self, intf, rename=False, **kwargs ):
        "Add (and reparent) an interface"
        OVSSwitch.addIntf( self, intf, **kwargs )
        intf.node = self
        if rename:
            self.renameIntf( intf )

    def attach( self, intf ):
        "Attach an interface and set its port"
        port = self.ports[ intf ]
        if port:
            if self.isOldOVS():
                self.cmd( 'ovs-vsctl add-port', self, intf )
            else:
                self.cmd( 'ovs-vsctl add-port', self, intf,
                          '-- set Interface', intf,
                          'ofport_request=%s' % port )
            self.validatePort( intf )

    def validatePort( self, intf ):
        "Validate intf's OF port number"
        ofport = int( self.cmd( 'ovs-vsctl get Interface', intf,
                                'ofport' ) )
        if ofport != self.ports[ intf ]:
            warn( 'WARNING: ofport for', intf, 'is actually', ofport,
                  '\n' )

    def renameIntf( self, intf, newname='' ):
        "Rename an interface (to its canonical name)"
        intf.ifconfig( 'down' )
        if not newname:
            newname = '%s-eth%d' % ( self.name, self.ports[ intf ] )
        intf.cmd( 'ip link set', intf, 'name', newname )
        del self.nameToIntf[ intf.name ]
        intf.name = newname
        self.nameToIntf[ intf.name ] = intf
        intf.ifconfig( 'up' )

    def moveIntf( self, intf, switch, port=None, rename=True ):
        "Move one of our interfaces to another switch"
        self.detach( intf )
        self.delIntf( intf )
        switch.addIntf( intf, port=port, rename=rename )
        switch.attach( intf )


def printConnections( switches ):
    "Compactly print connected nodes to each switch"
    for sw in switches:
        output( '%s: ' % sw )
        for intf in sw.intfList():
            link = intf.link
            if link:
                intf1, intf2 = link.intf1, link.intf2
                remote = intf1 if intf1.node != sw else intf2
                output( '%s(%s) ' % ( remote.node, sw.ports[ intf ] ) )
        output( '\n' )


def moveHost( host, oldSwitch, newSwitch, newPort=None ):
    "Move a host from old switch to new switch"
    hintf, sintf = host.connectionsTo( oldSwitch )[ 0 ]
    oldSwitch.moveIntf( sintf, newSwitch, port=newPort )
    return hintf, sintf

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2 ):
        switch = self.addSwitch( 's1' )
        switch2 = self.addSwitch( 's2' )
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost( 'h%s' % (h + 1),
                             cpu=.5/n )
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            self.addLink( host, switch, bw=2, delay='50ms', loss=1,
                          max_queue_size=1000, use_htb=True )
            
            self.addLink( host, switch2, bw=3, delay='10ms', loss=0,
                              max_queue_size=1000, use_htb=True )

class MyTopo( Topo ):
    "Linear topology of k switches, with n hosts per switch."

    def build( self, **_opts):
        """k: number of switches
           n: number of hosts per switch"""


        genHostName = lambda i, j: 'h%s' % i
        
        switch_list = []
        for i in irange( 1, 3 ):
            # Add switch
            switch = self.addSwitch( 's%s' % i )
            # Add hosts to switch
            if i != 4:
                host = self.addHost( genHostName( i, 1 ) )
                self.addLink( host, switch )
            switch_list.append(switch)
            # Connect switch to previous
        s1 = switch_list[0]
        s2 = switch_list[1]
        s3 = switch_list[2]
        #'''
        
        self.addLink( s2, s1, bw=2, delay='50ms', loss=3,
                      max_queue_size=1000, use_htb=True )
        self.addLink( s2, s3, bw=3, delay='10ms', loss=1,
                      max_queue_size=1000, use_htb=True )
        #'''

def mobilityTest():
    "A simple test of mobility"
    info( '* Simple mobility test\n' )
    net = Mininet( topo=MyTopo(), switch=MobilitySwitch, link=TCLink )
    #net = Mininet( topo=SingleSwitchTopo( 3 ), switch=MobilitySwitch, link=TCLink )
    #switch2 = net.addSwitch( 's2' )
    #net.addLink( net.get('h2'), switch2,bw=10, delay='1ms', loss=1,
    #                      max_queue_size=1000, use_htb=True)
    info( '* Starting network:\n' )
    net.start()
    #net.get('h1').cmd('ifconfig > ifconfig1')

    printConnections( net.switches )
    info( '* Testing network\n' )
    net.pingAll()
    #net.delLinkBetween(net.get('h1'),net.get('s2'))
    #net.pingAll()

    info( '* Identifying switch interface for h1\n' )
    h1, h2 = net.get( 'h1', 'h2' )
    s1, s2 = net.get( 's1', 's2' )
    h2.cmd('tcpdump -i h2-eth0 -w server.pcap &')
    h1.cmd('tcpdump -i h1-eth0 -w client.pcap &')
    #for s in 2, 3, 1:
    s = 3
    old, new = net.get( 's1', 's3' )
    new = net[ 's%d' % s ]
    port = randint( 10, 20 )
    
    
    net.get('h2').cmd('bash mn_server.sh &')
    
    time.sleep(5)

    startTime = time.time()
    print startTime
    net.get('h1').cmd('bash mn_client.sh &')
    print time.time() - startTime
    time.sleep(5)
    print time.time() - startTime
    
    info( '* Moving', h1, 'from', old, 'to', new, 'port', port, '\n' )
    hintf, sintf = moveHost( h1, old, new, newPort=port )

    print time.time() - startTime
    info( '*', hintf, 'is now connected to', sintf, '\n' )

    for sw in net.switches:
        sw.dpctl( 'del-flows' )
    #info( '* New network:\n' )
    #printConnections( net.switches )
    #info( '* Testing connectivity:\n' )
    #net.pingAll()
    print time.time() - startTime
    time.sleep(20)

    net.stop()
    

if __name__ == '__main__':
    setLogLevel( 'info' )
    mobilityTest()
