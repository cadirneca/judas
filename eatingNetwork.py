import pyshark  # to analyse pcap
import pygraphviz as pgv  # dot files
import re
from colorama import Fore, Style
import ipinfo
import ipapi
from pprint import pprint
import eatingJson as eatjson
import json
import urllib


# ------------------------------
#       PCAP ANALYSIS
# ------------------------------

def generaGraph (pcapfile, macgraph, ipgraph):
    # Prepare .dot
    G1 = pgv.AGraph(directed=True)  # MACs
    G2 = pgv.AGraph(directed=True)  # IPs

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)

    print("Reading pcap file to generate the graph of connections. Check files: %s and %s" % (macgraph, ipgraph))
    pnumber = 0
    nodelist = []
    mac_ips = {}
    for pkt in cap:
        pnumber = pnumber + 1  # number of packets

        # Get MAC address
        src = pkt.eth.src  # pkt.ip.src # source
        dst = pkt.eth.dst  # pkt.ip.dst # destination

        matching = [s for s in nodelist if src in s]
        if (not matching):
            nodelist.append(src)
            G1.add_node(src)  # G.add_node('a')

        matching = [s for s in nodelist if dst in s]
        if (not matching):
            nodelist.append(dst)
            G1.add_node(dst)  # G.add_node('a')

        G1.add_edge(src, dst)  # Add edge to the graph of MACs

        # Get IP (if available)
        if ("IP" in str(pkt.layers)):
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst

            iplistsrc = mac_ips.get(src, [])
            iplistdst = mac_ips.get(dst, [])

            matching = [s for s in iplistsrc if src_ip in s]
            if (not matching): iplistsrc.append(src_ip)
            matching = [s for s in iplistdst if dst_ip in s]
            if (not matching): iplistdst.append(dst_ip)

            mac_ips.update({src: iplistsrc, dst: iplistdst})  # add values to the dictionary
            G2.add_edge(src_ip, dst_ip)

    # print("%s" % mac_ips)
    # Make subgraphs
    ncol = len(mac_ips)
    legend = []
    for x in mac_ips:
        ips = mac_ips.get(x)
        if (len(ips) > 1):
            legend.append(x)
            for i in ips:
                G2.add_node(i, color='blue')  # , fillcolor='burlywood1')

        # G2.add_subgraph(ips,label=x.replace('"', "'")) #IPs in the same graph

    # Make a legend:
    # print("%s" % legend)
    # G2.add_subgraph(legend, name='Legend', label='Legend')

    # Plot graph
    # print(G)
    G1.write("results/mac.dot")
    G2.write("results/ip.dot")

    G1.layout()  # default to neato
    G1.layout(prog='dot')  # use dot
    G2.layout()  # default to neato
    G2.layout(prog='dot')  # use dot

    G1.draw(macgraph)  # dot.render('test-output/round-table.gv', view=True)
    G2.draw(ipgraph)
    # G.draw('file.ps',prog='circo') # use circo to position, write PS file

    return mac_ips


def findInPcap(pcapfile,macs,ips,words):
    "finds a list of MACS, IPs and words in the data in a PCAP file extended list of elements."
    extended = []
    extended.extend(macs)
    extended.extend(ips)
    extended.extend(words)

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)
    rx = re.compile('|'.join(extended))

    print("Reading pcap file to find relevant data")
    pnumber = 0
    found = []
    finded = ""
    for pkt in cap:
        pnumber = pnumber + 1  # number of packets analysed

        # Get MAC address
        src = pkt.eth.src  # pkt.ip.src # source
        dst = pkt.eth.dst  # pkt.ip.dst # destination

        if(rx.match(src)):
            found.append(src)
            finded = finded + "\n     MAC(src): %s" % (src)

        if(rx.match(dst)):
            found.append(dst)
            finded = finded + "\n     MAC(dst): %s" % (dst)

        # Check IP if available
        if ("IP" in str(pkt.layers)):
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst

            if (rx.match(src_ip)):
                found.append(src_ip)
                finded = finded + "\n     IP(src): %s with MAC %s" % (src_ip, src)
            if (rx.match(dst_ip)):
                found.append(dst_ip)
                finded = finded + "\n     IP(dst): %s with MAC %s" % (dst_ip, dst)

        if(len(found)>0):
            print(Fore.BLUE, end='')
            print("** Searching in packet number: %d ..." % (pnumber))
            print(Style.RESET_ALL)
            print(finded)
            print("     Summary:%d ", found)
            print(Fore.YELLOW, end='')
            print("     End with %d matches." % (len(found)))
            print(Style.RESET_ALL)
            found = []
            finded = ""


def findInPcap2(pcapfile,macs,ips,words):
    "finds a list of MACS, IPs and words in the data in a PCAP file extended list of elements."
    extended = []
    extended.extend(macs)
    extended.extend(ips)
    extended.extend(words)

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)
    rx = re.compile('|'.join(extended))

    print("Reading pcap file to find relevant data")

    pnumber = 0
    dictosumary = {}
    matches = 0  # number of matches in this packet
    for pkt in cap:
        pnumber = pnumber + 1  # number of packets analysed

        # Get MAC addresses
        src = pkt.eth.src  # pkt.ip.src # source
        dst = pkt.eth.dst  # pkt.ip.dst # destination

        # Get IP addresses if available
        if ("IP" in str(pkt.layers)):
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
        else:
            src_ip = ''
            dst_ip = ''

        lst = [src, dst, src_ip, dst_ip]

        for i in lst:
            if(rx.match(i)):
                val = dictosumary.get(i)
                if(val==None):
                    val = [pnumber]
                else:
                    val.append(pnumber)
                dictosumary.update({i:val})
                matches +=1

    for k in dictosumary:
        values = dictosumary.get(k)
        print("** Results for: ",end='')
        print(Fore.BLUE,end='')
        print(k)
        print(Style.RESET_ALL)
        print(values)

    print(Fore.YELLOW, end='')
    print("Total matches: ", matches)
    print(Style.RESET_ALL)


def getInfoIP (IPlist,printJson=False):
    "Returns a list with information about public IPs"
    if not isinstance(IPlist, list):
        return []

    infoIPs = []
    for i in IPlist:
        if ipinfo.ispublic(i):
            print('Public IP: %s' % i)
            # search info:
            info = ipapi.location(i)
            if info is not None:
                # process as Address
                jsonarray = json.dumps(info)
                if printJson: pprint(jsonarray)
                a = json.loads(jsonarray, object_hook=eatjson.Address.as_address)

                if isinstance(a, eatjson.Address):
                    infoIPs.append(a)
                    #print(a)
            else:
                print('     (No info)')
        else:
            print('Private IP: %s' % i)

    return infoIPs


def getInfoIPVT (IPlist, apiKey):
    "Returns a list with information about public IPs returned by VirusTotal"
    if not isinstance(IPlist, list):
        return []

    infoIPs = []
    url = 'https://www.virustotal.com/vtapi/v2/ip-address/report'
    strres = ''
    for i in IPlist:
        if ipinfo.ispublic(i):
            print('Public IP: %s' % i)
            # search info:
            parameters = {'ip':i , 'apikey': apiKey}
            print('%s?%s' % (url, urllib.parse.urlencode(parameters)))
            try:
                with urllib.request.urlopen('%s?%s' % (url, urllib.parse.urlencode(parameters))) as url:
                    info = url.read()
                response_dict = json.loads(info)
                pprint(response_dict)
                strres = "%s\n%s" % (strres,str(response_dict))
            except:
                print("   No info available...")

            if info is not None:
                None
                # process as Address
                #jsonarray = json.dumps(info)
                #a = json.loads(jsonarray, object_hook=eatjson.Address.as_address)

                #infoIPs.append(a)
                #print(a)
            else:
                print('     (No info)')
        else:
            print('Private IP: %s' % i)

    return strres

