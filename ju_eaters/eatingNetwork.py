######
# @author:      Ana Nieto
# @country:     Spain
# @website:     https://www.linkedin.com/in/ananietojimenez/
######

import pyshark  # to analyse pcap
import pygraphviz as pgv  # dot files, install graphviz first
import re
from colorama import Fore, Style
from auxiliar.external import ipinfo
import ipapi
from pprint import pprint
from ju_eaters import eatingJson as eatjson
import json
import urllib
from auxiliar import auxiliar as aux
import os
import sys
from bs4 import BeautifulSoup
import nfstream

# ------------------------------
#       PCAP ANALYSIS
# ------------------------------

def generaGraph (pcapfile, macgraph, ipgraph, pathresults = 'results'):
    """
    Genera graphs for connections between IPs and MAC addresses. This function also can be used to read the MACs and
    IPs in the .pcap or .pcapng file.
    :param pcapfile: path to the .pcap or .pcapng file
    :param pathresulst: path to save additional results
    :param macgraph: path to the .png file for the graph of MAC
    :param ipgraph: path to the .png file for the graph of IPs
    :param plot: True if the graphs must be generated (True by default)
    :return: dictionary with macs and IPs idenntified to be used in other functions
    """
    # Prepare .dot
    G1 = pgv.AGraph(directed=True)  # MACs
    G2 = pgv.AGraph(directed=True)  # IPs

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)
    if cap is None or len(cap)==0:
        print('Empty .pcap')
        return None

    print("Reading pcap file to generate the graph of connections. ")
    if macgraph is not None:
        print("- Generating graph for MAC addresses in: %s" % macgraph)
    if ipgraph is not None:
        print("- Generating graph for IP addresses in: %s" % ipgraph)

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

    G1.write(pathresults + "/mac.dot")
    G2.write(pathresults + "/ip.dot")

    G1.layout()  # default to neato
    G1.layout(prog='dot')  # use dot
    G2.layout()  # default to neato
    G2.layout(prog='dot')  # use dot

    if macgraph is not None:
        G1.draw(macgraph)  # dot.render('test-output/round-table.gv', view=True)

    if ipgraph is not None:
        G2.draw(ipgraph)
        # G.draw('file.ps',prog='circo') # use circo to position, write PS file

    return mac_ips

def searchStrings(pcapfile, words, printresults=True, output_dir=None):
    """
    Finds a list of strings in the data of the pcapfile
    :param pcapfile: path to the pcapfile
    :param words: words to be searched
    :param printresults: if True (by default) the method prints the results
    :param output_dir: folder to save the results
    :return: ID of the packet and also prints the results by default
    """

    #Get pcap:
    cap = pyshark.FileCapture(pcapfile)

    if output_dir is not None:
        print(' The results (if any) will be saved in %s ' % output_dir)

    pnumber = -1
    found = []

    for pkt in cap:
        pnumber = pnumber + 1  # number of packets analysed


        # Get data - http
        if ("HTTP" in str(pkt.layers)):
            http = pkt.http

            if http.get('content_length') is not None and int(http.content_length)>0:
                codification = http.content_type
                encoded_data = http.file_data

                #read data:
                if codification.find('application/x-www-form-urlencoded'):
                    data = urllib.parse.unquote(encoded_data)
                elif codification.find('application/json'):
                    data = encoded_data # we can do the search in this way
                elif codification.find('text/html'):
                    data = BeautifulSoup(encoded_data)

                #search for words:
                if any(x in data for x in words):
                    filename = '%d.txt' % pnumber
                    found += [(pnumber, pkt, filename)]

                    if output_dir is not None:
                        summaryfile = "%s/%s" % (output_dir,filename)
                        aux.saveDataIntoFile(summaryfile, data)

    if len(found)>0:
        head = "Results for strings %s:\n     Packet number   Summary" \
              "\n     -------------   ---------------------------" % words
        body = ''

        for t in found:
            n = t[0]
            p = t[1]
            if ("IP" in str(p.layers)):
                com_dirs = 'src:%s, dst:%s' % (p.ip.src,  p.ip.dst)

            else:
                com_dirs = 'src:%s, dst:%s' % (p.eth.src,  p.eth.dst)

            summary = '%s,%s' % (com_dirs,p.layers)
            body += '     %d  %s\n' % (n, summary)

    else:
        head = 'There are not matches with strings: %s' % words
        body = ''

    data = "%s\n%s" % (head, body)
    if printresults:
        print(head)
        print(body)

    if output_dir:
        aux.saveDataIntoFile("%s/%s" % (output_dir,'SUMMARY.txt'), data)

    return found





def findInPcap(pcapfile,macs=[],ips=[],words=[]):
    """
    Finds a list of MACS, IPs and words in a PCAP file extended list of elements.
    :param pcapfile: path to the pcapfile
    :param macs: list of macs to be searched (if any)
    :param ips: list of IPs to be searched (if any)
    :param words: list of words to be searched (if any)
    :return: prints the results
    """
    extended = []
    extended.extend(macs)
    extended.extend(ips)
    extended.extend(words)

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)
    rx = re.compile('|'.join(extended))

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


def findInPcap2(pcapfile,macs=[],ips=[],words=[]):
    """
    Finds a list of MACS, IPs and words in a PCAP file extended list of elements.
    :param pcapfile: path to the pcapfile
    :param macs: list of macs to be searched (if any)
    :param ips: list of IPs to be searched (if any)
    :param words: list of words to be searched (if any)
    :return: prints the results
    """
    extended = []
    extended.extend(macs)
    extended.extend(ips)
    extended.extend(words)

    # Get pcap
    cap = pyshark.FileCapture(pcapfile)
    rx = re.compile('|'.join(extended))

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


def getInfoIP (IPlist,printJson=False, onlyPrint=False):
    """
    Get information about the IPs in the list, if the IP is public then this method searches public information about
    the IP
    :param IPlist: list of IPs to be analysed
    :param printJson: if True, then the info is saved in a .json file (False by default)
    :param onlyPrint: if True, then this method only prints the results in the terminal (False by default)
    :return: if onlyPrints is False this method returns a list of Addresses with the public information about public
        addresses. Check JUDAS specification to understand the expected format for Address object.
    """

    if not isinstance(IPlist, list):
        return []

    infoIPs = []

    for i in IPlist:
        if ipinfo.ispublic(i):
            print('Public IP: %s, results:' % i)
            # search info:
            info = ipapi.location(i)
            if info is not None:
                if onlyPrint:
                    print(Fore.BLUE, end='')
                    if len(info)==0:
                        print('none')
                    else:
                        print(info)
                    print(Style.RESET_ALL, end='')
                else:
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
    """
    :param IPlist: list with public & private IPs
    :param apiKey: API key for using VT
    :return: list with information about public IPs returned by VirusTotal
    """
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

            if info is None:
                print('     (No info)')
        else:
            print('Private IP: %s' % i)

    return strres




# ------------------------------
#       MAIN METHOD
# ------------------------------
if __name__ == "__main__":
    """
    Example: python3 eatingNetwork.py sources/network/dfrws_police.pcap
    """
    options = ["Load .pcap file", "Generate graph", "Print network identifiers (MAC and IP)",
               "Check IP public info", "Find", "Extract objects", "Print flow NFS"]
    max_options = len(options)

    if len(sys.argv) > 1:
        file = sys.argv[1]
        if not aux.checkExtension(file, extensions="pcap,pcapng"):
            # Ask for .pcap file:
            file = aux.getPathToFile(msg='Please, provide a valid file:',file_type='pcap,pcapng')
    else:
        # Ask for .pcap file:
        file = aux.getPathToFile(type_file='pcap,pcapng')

    # Show options:
    ans = aux.showOptions(options)

    mac_ip = None
    while ans <= max_options:

        if ans == 1:    #Load .pcap file
            file = aux.getPathToFile(type_file='pcap')
            mac_ip = None

        elif ans == 2:  #Genera graph
            file_directory = os.path.dirname(file)

            macgraph = file_directory + '/macgraph.png'
            ipgraph = file_directory + '/ipgraph.png'
            mac_ip = generaGraph(file, macgraph, ipgraph)

        elif ans == 3:  #Print network identifiers (MAC and IP)
            if mac_ip is None:
                mac_ip = generaGraph(file, macgraph=None, ipgraph=None)
            print(mac_ip)

        elif ans == 4:  #Check IP public info
            if mac_ip is None:
                mac_ip = generaGraph(file, macgraph=None, ipgraph=None)
            # get all IPs:
            iplist = mac_ip.values()
            iplist = [x for list in mac_ip.values() for x in list] # unique list of IPs
            ip_public = [x for x in iplist if ipinfo.ispublic(x)]

            getInfoIP(ip_public, onlyPrint=True)

        elif ans == 5:   #Find
            ans = input("Provide the words to be searched separated by commas (e.g. malaga,spain,blue):")
            words = ans.split(",")
            output_dir = input("Please, provide a folder to save the results (%s/output_find by default):" % (os.getcwd()))
            if len(output_dir)==0 or  (os.path.exists(output_dir) and not os.path.isdir(output_dir)):
                output_dir = os.getcwd()+"/output_find"

            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            print('Using %s as output directory' % output_dir)
            print("   ** Searching for: %s" % words)
            searchStrings(file, words=words, output_dir=output_dir)

        elif ans ==6:   #Extract objects
            "To be done..."
            # path_folder = aux.getPathToFolder()
            # Extract objects

        elif ans == 7: # NFEntry
            stream = nfstream.NFStreamer(source=file)

            for flow in stream:
                print(flow)

        input("Press enter to continue...")
        ans = aux.showOptions(options)



