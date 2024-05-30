from mininet.topo import Topo
import mininet
import random
import os

RED_CORRECTION_FACTOR = { # Need to correct for the distortions that the Linux RED implementation creates
    0.5: 83/79,
    1.0: 83/75,
    2.0: 83/69,
    3.0: 83/68,
    4.0: 83/58,
    5.0: 83/68,
    6.0: 83/58,
    7.0: 83/51
}

class BottleneckTopology( Topo ):
    # Buffer size expressed in packets, patency in ms, capacity in Mbps
    # BW Delay product also in packets
    def __init__( self, srcHosts=3, linkCapacity=100, linkLatency=3, bufferFactor=1, bw_delay_product=100, random_latency_range=None, use_htb=True, use_red=False, accessCapacity=120):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add Source
        src_hosts = []
        dst_hosts = []
        for i in range(1, srcHosts+1):
            src_hosts.append(self.addHost('h'+str(i)))
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        for i in range(srcHosts+1, 2*srcHosts+1 ):
            dst_hosts.append(self.addHost('h'+str(i)))
        

        # Add links between source hosts and switch s1
        random.seed(1)
        e2e_latencies = []
        for h in src_hosts:
            if random_latency_range is None:
                self.addLink(s1, h)
            else:
                random_latency = int(random.uniform(random_latency_range[0], random_latency_range[1]) * 10) / 10
                e2e_latencies.append(2*random_latency + 2*linkLatency)
                self.addLink(s1, h, bw=accessCapacity, delay=str(random_latency) + "ms")
        
        # Add links between destination hosts and switch s2
        for h in dst_hosts:
            if random_latency_range is None:
                self.addLink(s2, h)
            else:
                random_latency = int(random.uniform(random_latency_range[0], random_latency_range[1]) * 10) / 10
                e2e_latencies[-1] += 2*random_latency
                self.addLink(s2, h, bw=accessCapacity, delay=str(random_latency) + "ms")

        print(e2e_latencies)
        
        # delay, max_queue_size are led directly to tc-netem tool as: delay and limit.
        # Could also add: jitter or loss
        # Therefore: follow netem config: packet size is expressed as number of packets
        # Add link between switches s1 and s2
        #link_size = bw_delay_product * RED_CORRECTION_FACTOR[bufferFactor] if use_red else bw_delay_product
        self.addLink(s1, s2, bw=linkCapacity, delay=str(linkLatency) + "ms",
                     max_queue_size=int(bufferFactor * bw_delay_product) + bw_delay_product,
                     enable_red=use_red)