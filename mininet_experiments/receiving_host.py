#!/usr/bin/python3

import sys
import time
import subprocess
from pyroute2 import IPRoute
import yaml
import os

RESULT_FILE_PREFIX = ''

def initiateLog(desthostID):
    if os.path.exists(RESULT_FILE_PREFIX+f"hostlogs/h{desthostID}.log"):
        return
    with open(RESULT_FILE_PREFIX+f"hostlogs/h{desthostID}.log", "w+") as logfile:
        logfile.write(("%.6f" % time.time())+": h{desthostID}: Started\n")


def log(logContent):
    with open(RESULT_FILE_PREFIX+f"hostlogs/h{desthostID}.log", "a+") as logfile:
        logfile.write(("%.6f" % time.time())+f": h{desthostID}: "+logContent+"\n")


def startTcpDump(desthostID):
    # > '+RESULT_FILE_PREFIX+f'hostdata/h{desthostID}-eth'+str(i)+'.log
    for i in range(1):
        with open(RESULT_FILE_PREFIX+f'hostdata/h{desthostID}-eth'+str(i)+'.log', 'w+') as f:
            tcpDumpCommmand = (f'tcpdump -tt -i h{desthostID}-eth'+str(i)+' -e -v -n -S -x -s 96').split()
            subprocess.Popen(tcpDumpCommmand, stdout=f, stderr=f)
            log("Started tcpdump.")


# Start iperf server with TCP on destination hosts
def startTcpServer(config):
    resfile = config['result_dir'] + config['iperf_outfile_server_tcp']
    samplingperiod = config['iperf_sampling_period_server']
    fout = open(resfile, "w")
    tcpIperfCommand = ('iperf -s -p 5002 -e -i %d -t %d -f %s' % (samplingperiod, config['send_duration'] + 5, config['iperf_outfile_format'])).split()
    print(tcpIperfCommand)
    log("Starting TCP Server.")
    log("Command: " + str(tcpIperfCommand))
    proc = subprocess.Popen(tcpIperfCommand, stdout=fout)
    return proc, fout

# Start iperf server with UDP on destination hosts
def startUdpServer(config):
    resfile = config['result_dir'] + config['iperf_outfile_server_udp']
    samplingperiod = config['iperf_sampling_period_server']
    fout = open(resfile, "w")
    udpIperfCommand = ('iperf -s -p 5003 -u -e -i %d -t %d -f %s' % (samplingperiod, config['send_duration'] + 10, config['iperf_outfile_format'])).split()
    print(udpIperfCommand)
    log("Starting UDP Server.")
    log("Command: " + str(udpIperfCommand))

    proc = subprocess.Popen(udpIperfCommand, stdout=fout)
    return proc, fout


# # Setup second interface (only needed in multipath cases)
# def setupInterface(hostID):
#     ip = IPRoute()
#     index = ip.link_lookup(ifname=f'h{desthostID}-eth1')[0]
#     ip.addr('add', index, address='10.0.1.'+hostID, mask=24)
#     ip.close()

def main(config, desthostID, nSrc):
    global RESULT_FILE_PREFIX
    RESULT_FILE_PREFIX = config['result_dir']
    initiateLog(desthostID)

    # Announce yourself
    # h{desthostID}-eth0
    srcID = desthostID
    # here it is advertising it's own ip. ips are the opposite of node numbers 
    pingCommand = ("ping -c 3 -I %s-eth%d 10.0.%d.%d" % ("h"+str(desthostID), 0, 0,(desthostID))).split()
    subprocess.call(pingCommand)

    use_tcp = False
    use_udp = False
    protocols = [[a['protocol'] for a in client.values()][0] for client in config['sending_behavior']]
    for prot in protocols:
        if "tcp" in prot:
            use_tcp = True
        if "udp" in prot:
            use_udp = True

    log("Use TCP: " + str(use_tcp) + " | Use UDP: " + str(use_udp))
    startTcpDump(desthostID)
    if use_tcp:
        tcp_proc, tcp_f = startTcpServer(config)
    if use_udp:
        udp_proc, udp_f = startUdpServer(config)
    if use_tcp:
        tcp_proc.communicate()
        tcp_f.close()
        log("Finished TCP Server.")

    if use_udp:
        udp_proc.communicate()
        udp_f.close()
        log("Finished UDP Server.")

 
def parseargs():
    desthostID = int(sys.argv[1])
    configfile_location = sys.argv[2]
    nSrc = int(sys.argv[3])
    return desthostID, configfile_location, nSrc

if __name__ == "__main__":
    desthostID, configloc, nSrc = parseargs()
    f = open(configloc, "r")
    config = yaml.safe_load(f)
    f.close()
    main(config, desthostID, nSrc)