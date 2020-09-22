######
# @author:      Ana Nieto
# @country:     Spain
# @website:     https://www.linkedin.com/in/ananietojimenez/
######

from email.message import EmailMessage
# https://github.com/Thx3r/Emlx_Parser
import pprint
import os
import pygraphviz as pgv  # dot files
import networkx as nx
from networkx.readwrite import json_graph
from auxiliar.external import ipinfo, http_server
import json
import sys
from auxiliar import auxiliar as aux
from ju_eaters import eatingJson as ejson

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = current_dir + '/..'
sys.path.insert(0, current_dir)
sys.path.insert(0,app_dir)


####################################
#           CLASS SERVER
####################################
class Server():
    LAST_ID = -1

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, dicto):
        self.id = Server.LAST_ID + 1
        Server.LAST_ID += 1
        self.name = dicto.get('name')
        self.ip = dicto.get('ip')

        # check:
        if self.ip is None: self.ip = ''
        if self.name is None: self.name = self.ip

    # ---------------------------------
    #       METHODS TO CONSTRUCT THE GRAPH
    # ---------------------------------
    def getID(self): return self.id

    def getIP(self): return self.ip

    def getName(self): return self.name

    def getLabel(self): return 'name:%s\nip:%s' % (self.name, self.ip)

    def getGroup(self): return 1

    def getColor(self): return 'darkviolet'


    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        tbp = 'Name:%s, IP:%s\n' % (self.name,self.ip)
        return tbp


class Email():
    LAST_ID = -1
    [FROM, TO, SUBJECT, SOURCE_SERVER, SPF, SERVERS, CONTENT] = ['From', 'To', 'Subject', 'SourceServer',
                                                                 'Received-SPF', 'Servers', 'Content']
    DICTO = {'From':'',
             'To':'',
             'Subject':'',
             'SourceServer':'',
             'Received-SPF':{'type':'', 'identity':'', 'client-ip':'','helo':'', 'envelope':'','receiver':''},
             'Servers':[],
             'Content':''}
    EXTENSIONS = 'eml'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, input):
        self.id = Email.LAST_ID + 1
        Email.LAST_ID += 1
        self.dicto = Email.getDicto()

        if aux.isFile(input) and aux.checkExtension(input, Email.EXTENSIONS):
            # Parse
            parsed = parseEmail(file, printjson=False)

            self.setFrom(getEmisor())
            self.setTo(getReceptor())
            self.setSubject(parsed.get('Subject'))
            self.setSourceServer(getSourceServer(parsed))
            #self.setSPF(getSPF(parsed_email))
            self.setServers(getServerList(parsed))
            #self.setContent(getContent(parsed))

        else:
            raise ValueError('class Email not initiated properly id: %s - check innput file type' % self.id)


    # ---------------------------------
    #       STATIC METHODS
    # ---------------------------------
    @staticmethod
    def getDicto():
        return Email.DICTO

    @staticmethod
    def isDicto(dicto):
        # Check dicto:
        if type(dicto) is not dict:
            return False
        if all(k in Email.DICTO for k in dicto.keys):
            # check also keys in spf:
            kspf = dicto.get('Received-SPF').keys()
            if all(k in Email.DICTO.get('Received-SPF').keys() for k in kspf):
                return True

        return False


    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getID(self):
        return self.id

    def getSource(self):
        return self.source

    def getDestination(self):
        return self.destination

    def getSubject(self):
        return self.source

    def getSPF(self):
        return self.spf

    def getServers(self):
        return self.servers

    def getContent(self):
        return self.content

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def setSourceServer(self, server):
        if type(server) is Server:
            self.dicto.update({'Source':server})


    def setDicto(self, dicto):
        """
        Update values using a dicto structure
        :param dicto: dicto structure (check isDicto() first)
        :return:
        """
        if not self.isDicto(dicto):
            return False

        # Set values:
        self.source = dicto.get('Source')
        self.destination = dicto.get('Destination')
        self.subject = dicto.get('Subject')
        self.spf = dicto.get('Received-SPF')
        self.servers = dicto.get('Servers')
        self.content = dicto.get('Content')


# ------------------------------------------------------
#   EMAIL ANALYSIS
# ------------------------------------------------------

def parseEmail(file, printjson=True):
    """
    Ref: https://pypi.org/project/eml-parser/
    Returns information about the email (.eml)
    :param file: file with extension .eml (email saved).
    :param printjson: True (by default) prints the result
    :return: file parsed as json
    """
    # Parse email from file:
    with open(file, 'rb') as fhdl:
        raw_email = fhdl.read()

    parsed_eml = external.eml_parser.eml_parser.decode_email_b(raw_email, include_raw_body=True, include_attachment_data=True)

    # This is the file as json
    if printjson:
        pprint.pprint(parsed_eml)

    # Returns the eml parsed:
    return parsed_eml


def parseEmail2(file, printjson=True):
    """
    Only for testing
    Ref: https://docs.python.org/3/library/email.examples.html
    :param file: file to be read
    :param printjson: True (by default) prints the result
    :return: file parsed as json
    """
    # Parse email from file:
    with open(file) as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read())

    richest = msg.get_body()

    return msg


def getEmisor(parsed_email):
    if type(parsed_email) is not dict:
        return None
    # Get string
    strcad = parsed_email.get('header').get('header').get('from')[0]
    print(strcad)
    # Separate name and email:
    name = aux.getSubstringDelimited('', '<', strcad)
    email = aux.getSubstringDelimited('<', '>', strcad)
    user = ejson.User(None, name)
    user.setEmail(email)
    return user

def getReceptor(parsed_email):
    if type(parsed_email) is not dict:
        return None

    # Get string
    strcad = parsed_email.get('header').get('header').get('to')[0]
    # Separate name and email:
    name = aux.getSubstringDelimited('', '<', strcad)
    email = aux.getSubstringDelimited('<', '>', strcad)
    user = ejson.User(None, name)
    user.setEmail(email)
    return user

def getServerList(parsed_email, debug=False):
    """
    Returns the list of servers in the email parsed as json
    :param parsed_email: json with the expected structure (see printEmailInfo)
    :param debug: False (by default). If True prints the info about the servers identified
    :return: list fo servers in the .eml file
    """
    if not isinstance(parsed_email, dict):
        return []

    recv_list = parsed_email.get('header').get('received')
    res = []
    server_info = {}

    for s in recv_list:
        name_server = s.get('by')[0]
        if server_info.get(name_server) is None:
            server_info.update({name_server:''})

        if s.get('from') is not None:
            name_from = s.get('from')[0] #aux.getSubstringDelimited('from', ' (', src)
            ip_from = s.get('from')[1] #aux.getIPs(src)

            if ipinfo.ispublic(name_from):
                # this can be the public IP of the source
                ip_from = name_from
                name_from = s.get('from')[1]

            server_info.update({name_from:ip_from})
        else:
            name_from = None
            ip_from = None

        if debug: print('-------------\nname_server:%s\nfrom:%s,%s\n' % (name_server, name_from, ip_from))

    for s in server_info:
        res += [Server({'name':s, 'ip':server_info.get(s)})]

    return res

def getSourceServer(parsed_email):
    """
    :param parsed_email: json with the expected structure (see printEmailInfo)
    :return: IP and name (if any) of the source server encapsulated in a Server class, None in other case
    """
    res = {}

    if not isinstance(parsed_email, dict):
        return []

    recv_list = parsed_email.get('header').get('received')

    info = recv_list[-1].get('src')

    ip = aux.getIPs(info)
    if len(ip)>0:
        res.update({'ip':ip})

    name = aux.getSubstringDelimited('from', ' (', info)

    if len(aux.getIPs(name))==0:
        res.update({'name':name})

    if len(res) > 0:
        return Server(res)

    return None


def getContent(parsed_email):
    content = parsed_email.get('body')[0].get('content')
    content_type = parsed_email.get('body')[0].get('content_type')
    return aux.Data(content,content_type)


def isFromMyBusinessNetwork(parsed_email):
    """
    If the source and destination share the same email server and are connected to the same access point, then
    the list of public IPs listed in the header are 0
    :param parsed_email: json with the expected structure (see printEmailInfo)
    :return: Local IP if the source and destination are in the same network with the same email server,
             None in other case.
    """
    if parsed_email.get('header').get('received_ip') is None:
        # get local IP of the sender
        return parsed_email.get('header').get('received')[0].get('from')[0]

    return None

def eatEmails(dirpath):
    """
    Process an email or a set of them depending on the format of the path. Epected formats:
    https://wiki.fileformat.com/email/
    https://sites.google.com/site/emailresearchorg/datasets

        # isolated emails
        EML     - Email Message File
        EMLX    - Apple Mail Message
        ICS     - iCalendar File Format
        MSG     - Microsoft Outlook Email Format
        OFT     - Microsoft Outlook Email Template

        # databaes:
        MBOX    - Email Mailbox Storage File
        OST     - Outlook Offline Storage File
        PST     - Personal Storage File
        TNEF    - Transport Neutral Encapsulation File
        VCF     - Virtual Contacts File
    :param filepath: path to the file to be processed
    :return: list of dictionaries (JSON structure), each one is for one email.
    """
    file = '.eml$|.emlx$'
    database = '.pst$|.mbox$'




def printBeautifulMail(filepath):
    """
    Shows an email in a friendly way for Ruben :)
    """

    # Take the name and extension of the file
    base = os.path.basename(filepath)
    name, extension = os.path.splitext(base)

    # parse email:
    parsed_email = parseEmail(filepath, printjson=False)

    # get sender
    parsed_email.get('header').get('from')

    # get info sender server
    source_server = getSourceServer(parsed_email)
    print('Source server:')
    print(source_server)

    # get list of servers
    print('List of (intermediary) servers:')
    servers = getServerList(parsed_email)
    print(servers)

    print('Creating graph...')
    # ---------
    # CREATE GRAPHS
    # ---------
    G1 = pgv.AGraph(directed=True)
    # Create list of nodes:
    nodes = ["%s(%s)" % (s.getName(), s.getIP()) for s in servers]
    G1.add_nodes_from(nodes)

    # Interactive graph
    G2 = nx.DiGraph(directed=True)
    nlist = []
    for s in servers:
        nlist = [s.getID()] + nlist
        G2.add_node(s.getID(), name=s.getLabel(), label=s.getName(),
                            group=s.getGroup(), color=s.getColor())

    # ---------
    # ADD RELATIONSHIPS
    # ---------
    nodes = nodes[::-1] #easy to assing
    i=0
    #while i<len(nodes)-1:
    #    G1.add_edge(nodes[i], nodes[i+1])

    G1.add_path(nodes)
    G2.add_path(nlist)

    # ---------
    # SAVE AND PRINT GRAPHS
    # ---------
    file1 = 'results/' + name + '.dot'
    G1.write(file1)
    G1.layout()  # default to neato
    G1.layout(prog='dot')  # use dot
    file2 = 'results/' + name + '.gif'
    G1.draw(file2)

    print('File saved in:\n%s\n%s' % (file1, file2))

    # G2 into JSON
    nx.draw(G2, with_labels=True)
    file3 = 'results/' + name + '.png'

    d = json_graph.node_link_data(G2)
    json.dump(d, open('auxiliar/force/forceEmail.json', 'w'))

    # Serve the file over http to allow for cross origin requests
    httpd = http_server.load_url('auxiliar/force/forceEmail.html')

    print('Interactive graph in http://localhost:8000/force/forceEmail.html')



# ------------------------------
#       MAIN METHOD
# ------------------------------
if __name__ == "__main__":
    """
    Example: python3 eatingEmail.py testing/emails/email.eml
    """
    options = ["Select email", "Print email (parsed)", "Print Graph", "Get source server", "Get servers info",
               "Get emisor (from)", "Get receptor (to)",
               "Check if the email was sent locally (without using the Internet)", "Print content"]
    max_options = len(options)

    if len(sys.argv) > 1:
        file = sys.argv[1]
        if not aux.checkExtension(file, extensions="eml"):
            # Ask for .eml file:
            file = aux.getPathToFile(msg='Please, provide a valid file:',file_type='eml')
    else:
        # Ask for .eml file:
        file = aux.getPathToFile(type_file='eml')

    # Parse email:
    parsed_email = parseEmail(file, printjson=False)

    # Show options:
    ans = aux.showOptions(options)

    while ans <= max_options:

        if ans == 1: # Select email
            file = aux.getPathToFile(type_file='eml')
            parsed_email = parseEmail(file, printjson=False)

        elif ans == 2: # Print parsed
            pprint.pprint(parsed_email)

        elif ans == 3: # Print graph
            printBeautifulMail(file)

        elif ans == 4: # Get source server
            print(getSourceServer(parsed_email))

        elif ans == 5: # Get hops
            sl = getServerList(parsed_email, debug=False)
            for s in sl: print(s)

        elif ans == 6: # Get emisor
            emisor = getEmisor(parsed_email)
            print(emisor.getCompleteName())
            print(emisor.getEmail())

        elif ans == 7: # Get receptor
            receptor = getReceptor(parsed_email)
            print(receptor.getCompleteName())
            print(receptor.getEmail())

        elif ans == 8: # Check if the email has been sent locally, without Internet connection
            localip = isFromMyBusinessNetwork(parsed_email)

            if localip:
                print('This email has been sent using the local email server - local ip:%s'%localip)
            else:
                print('This email was sent from outside my network')

        elif ans == 9: # Print content
            print(getContent(parsed_email))

        input("Press enter to continue...")
        ans = aux.showOptions(options)