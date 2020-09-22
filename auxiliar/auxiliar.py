######
# @author:      Ana Nieto
# @country:     Spain
# @website:     https://www.linkedin.com/in/ananietojimenez/
# This is for auxiliar methods that can be used in multiple files
######

import os
from colorama import Fore, Style
import datetime
import ipaddress
import requests
import pprint
import hashlib
import mysql.connector
from auxiliar.external import signature, exiftool
from tkinter import *


####################################
#       common classes
####################################

class Data():
    TYPE_TEXT = 'text/plain'

    TYPES = [TYPE_TEXT]

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, data, typetext, transfer_encoding='7bit'):
        self.data = data
        self.typetext = typetext

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getData(self):
        return self.data

    def getType(self):
        return self.typetext

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        tbp = self.data
        return tbp


class File():

    # keys for properties
    NAME = 'Name'
    DIRECTORY = 'root'
    FILEPATH = 'Path'
    MD5 = 'MD5'
    EXTENSION = 'Extension'

    # additional keys
    STRINGS = 'strings'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, filename, root=None):
        if root is None:
            root = os.getcwd()

        filepath = "%s/%s" % (root, filename)
        if not isFile(filepath):
            raise ValueError("Class file requires a filename")

        directory = getCurrentFolderIfNot(root)
        ext = getExtension(filepath)

        self.properties = {self.MD5:md5(filepath), self.NAME:filename, self.EXTENSION:ext, self.DIRECTORY:directory, self.FILEPATH:filepath,
                           self.STRINGS:[]}

    # ---------------------------------
    #       STATIC METHODS
    # ---------------------------------
    @staticmethod
    def getFiles(files):
        """
        :param files: list of paths given as strings
        :return: list of File
        """
        lfiles = []
        for f in files:
            head_tail = os.path.split(f)
            path = head_tail[0]
            name = head_tail[1]
            lfiles += [File(filename=name, root=path)]

        return lfiles

    @staticmethod
    def getKeyForProperties():
        """
        :return: properties used in all the objects
        the order will determine the order in the table
        """
        return [File.MD5, File.NAME, File.EXTENSION, File.DIRECTORY]


    @staticmethod
    def getTable(parent: object, files) -> object:
        """
        :param parent: frame where the object table will be placed
        :param files: list of File to be processed
        :return: new table for the files
        """
        # create a canvas object and a vertical scrollbar for scrolling it

        # use black background so it "peeks through" to
        # form grid lines
        scrolltab = ScrollbarFrame(parent)
        #parent.grid_rowconfigure(0, weight=1)
        #parent.grid_columnconfigure(0, weight=1)
        #parent.grid(row=0, column=0, sticky='nsew')

        frame = scrolltab.scrolled_frame

        properties = File.getKeyForProperties()

        #current_row = []
        #first row
        column = 0
        for p in properties:
            label = Label(frame, text="%s" % p, borderwidth=0, bg="black", fg="white")
            label.grid(row=0, column=column, sticky="nsew", padx=1, pady=1)
            #current_row.append(label)
            column = column + 1

        row = 1
        columns = len(properties)
        for f in files:
            if not isinstance(f, File):
                raise ValueError("Unexpected object in list of File")

            column = 0
            for p in properties:
                label = Label(frame, text="%s" % f.getProperty(p),
                                     borderwidth=0)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
            #    current_row.append(label)
                column = column +1
            #scrolltab._widgets.append(current_row)
            row = row + 1

        #for column in range(columns):
          #  scrolltab.grid_columnconfigure(column, weight=1)

        #vscrollbar.pack(side="right", fill="y")

        return scrolltab


    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getFilePath(self):
        return self.properties.get(self.FILEPATH)

    def getName(self):
        return self.properties.get(self.NAME)

    def getExtension(self):
        return self.properties.get(self.EXTENSION)

    def getFolder(self):
        return self.properties.get(self.DIRECTORY)

    def getMD5(self):
        return self.properties.get(self.MD5)

    def getProperties(self):
        return self.properties

    def getPath(self):
        return self.properties.get(self.FILEPATH)

    def getProperty(self, key):
        return self.properties.get(key)


    # ---------------------------------
    #       METHODS FOR MODIFICATION
    # ---------------------------------
    def calculateProperties(self):
        """
        Update the properties
        :return: new properties
        """
        fooExe = file(self.getPath(), 'r').read()
        strings = re.findall("[\x1f-\x7e]{4,}", fooExe)
        self.properties.update({self.STRINGS:strings})

        self.properties.update({self.MD5:md5(self.getPath())})

        return self.properties

    def addProperty(self, key, value):
        values = self.properties.get(key)
        if values is None:
            self.properties.update({key:value})
        else:
            # we already have some values...
            if isinstance(values, list):
                values = values + [value]
            else:
                values = [values, value]
            self.properties.update({key:values})


####################################
#       common methods
####################################

def isNumber(n):
    """
    checks if n is an integer
    :param n: value to be check
    :return: true if n is a number, false in other case
    """
    try:
        int(n)
        return True
    except ValueError:
        return False

def isFile(file):
    """
    Checks if a file exists
    :param file: name of the file
    :return: True if is a file, false in other case
    """
    return os.path.isfile(file)

def createFolder(name, path=None, printinfook=False):
    """
    :param name: name of the folder
    :param path: path to the folder (current path if none)
    :param printinfook: (prints info if all was ok)
    :return: this method creates a directory if not exists
    """
    if path is None: #get the current working directory
        path = os.getcwd()
    else:
        try:
            folderpath = "%s/%s" % (path, name)
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % folderpath)
        else:
            if printinfook: print("Successfully created the directory %s " % folderpath)


def deleteFolder(name, path=None, printinfook=False):
    """
    :param name: name of the folder
    :param path: path to the folder (current path if none)
    :param printinfook: (prints info if all was ok)
    :return: this method deletes a directory if not exists
    """
    if path is None: #get the current working directory
        path = os.getcwd()
    else:
        try:
            folderpath = "%s/%s" % (path, name)
            os.rmdir(path)
        except OSError:
            print("Deletion of the directory %s failed" % folderpath)
        else:
            if printinfook: print("Successfully deletion of directory %s " % folderpath)


def getSubstringDelimited(str_begin, str_finish, string):
    """
    Returns a string delimited by two strings
    :param str_begin: first string that is used as delimiter
    :param str_finish: second string used as delimiter
    :param string: string to be processed
    :return: string parsed, empty string if there are no matches
    """
    if len(str_begin) == 0:
        pos_beg = 0
    else:
        pos_beg = string.find(str_begin) + len(str_begin)

    pos_end = string.find(str_finish)

    if 0 <= pos_beg < len(string) and 0 <= pos_end < len(string):
        return string[pos_beg:pos_end]
    else:
        return ''


def isIP(str):
    """
    This method is inefficient, please try to change it using regular expressions
    :param str: string to be checked
    :return: True if str is valid as IPv4 or IPv6
    """
    try:
        ipaddress.ip_address(str)
        return True
    except:
        return False

def getIPv4(string):
    """
    Returns list of IPs in a string
    :param string: string to be processed
    :return: list of IPs
    """
    words = re.split('\[|\]|\)|\(|;|,| |\*| \n', string)
    # avoid duplicate values:
    words = list(dict.fromkeys(words))
    # avoid spaces:
    words = list(filter(lambda a: a != ' ', words))
    ip = []

    for w in words:
        if isIP(w): ip += [w]

    return ip

def getIPv6(string):
    IPV4SEG = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
    IPV4ADDR = r'(?:(?:' + IPV4SEG + r'\.){3,3}' + IPV4SEG + r')'
    IPV6SEG = r'(?:(?:[0-9a-fA-F]){1,4})'
    IPV6GROUPS = (
        r'(?:' + IPV6SEG + r':){7,7}' + IPV6SEG,  # 1:2:3:4:5:6:7:8
        r'(?:' + IPV6SEG + r':){1,7}:',  # 1::                                 1:2:3:4:5:6:7::
        r'(?:' + IPV6SEG + r':){1,6}:' + IPV6SEG,  # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
        r'(?:' + IPV6SEG + r':){1,5}(?::' + IPV6SEG + r'){1,2}',  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
        r'(?:' + IPV6SEG + r':){1,4}(?::' + IPV6SEG + r'){1,3}',  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
        r'(?:' + IPV6SEG + r':){1,3}(?::' + IPV6SEG + r'){1,4}',  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
        r'(?:' + IPV6SEG + r':){1,2}(?::' + IPV6SEG + r'){1,5}',  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
        IPV6SEG + r':(?:(?::' + IPV6SEG + r'){1,6})',  # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
        r':(?:(?::' + IPV6SEG + r'){1,7}|:)',  # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
        r'fe80:(?::' + IPV6SEG + r'){0,4}%[0-9a-zA-Z]{1,}',
        # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
        r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,
        # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
        r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
    )
    IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])  # Reverse rows for greedy match

    return re.findall(IPV6ADDR, string)

def getIPv4v6(string):
    """
    source: https://stackoverflow.com/questions/20286729/extract-ip-out-of-string-with-python
    :param string:
    :return: IPv6 matching with the string
    """
    ip6 = '''(?:(?x)(?:(?:[0-9a-f]{1,4}:){1,1}(?::[0-9a-f]{1,4}){1,6})|
    (?:(?:[0-9a-f]{1,4}:){1,2}(?::[0-9a-f]{1,4}){1,5})|
    (?:(?:[0-9a-f]{1,4}:){1,3}(?::[0-9a-f]{1,4}){1,4})|
    (?:(?:[0-9a-f]{1,4}:){1,4}(?::[0-9a-f]{1,4}){1,3})|
    (?:(?:[0-9a-f]{1,4}:){1,5}(?::[0-9a-f]{1,4}){1,2})|
    (?:(?:[0-9a-f]{1,4}:){1,6}(?::[0-9a-f]{1,4}){1,1})|
    (?:(?:(?:[0-9a-f]{1,4}:){1,7}|:):)|
    (?::(?::[0-9a-f]{1,4}){1,7})|
    (?:(?:(?:(?:[0-9a-f]{1,4}:){6})(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}))|
    (?:(?:(?:[0-9a-f]{1,4}:){5}[0-9a-f]{1,4}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}))|
    (?:(?:[0-9a-f]{1,4}:){5}:[0-9a-f]{1,4}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?:(?:[0-9a-f]{1,4}:){1,1}(?::[0-9a-f]{1,4}){1,4}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?:(?:[0-9a-f]{1,4}:){1,2}(?::[0-9a-f]{1,4}){1,3}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?:(?:[0-9a-f]{1,4}:){1,3}(?::[0-9a-f]{1,4}){1,2}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?:(?:[0-9a-f]{1,4}:){1,4}(?::[0-9a-f]{1,4}){1,1}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?:(?:(?:[0-9a-f]{1,4}:){1,5}|:):(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})|
    (?::(?::[0-9a-f]{1,4}){1,5}:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}))
    '''
    ip4 = '(?:[12]?\\d?\\d\\.){3}[12]?\\d?\\d'

    return re.findall(ip4 + '|' + ip6, string)

def json_serial(obj):
    """
    Ref: https://pypi.org/project/eml-parser/
    To show the components of the email in a beautiful way
    """
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

def getIPs(string):
    """
    Returns list of IPs in a string
    :param string: string to be processed
    :return: list of IPs
    """
    # return getIPv4v6(string)

    ip = getIPv4(string)
    if len(ip)==0:
        #try IPv6:
        return getIPv6(string)
    else:
        return ip

def getExtension(filepath):
    """
    :param filepath: path to the file
    :return: extension of a file
    """
    name, ext_file = os.path.splitext(filepath)
    ext_file = ext_file[1:]  # remove the point '.ext' -> 'ext'
    return ext_file

def checkExtension(filepath, extensions):
    """
    Checks if the file has an extension
    :param filepath: path to the file
    :param extensions: extension or list of extensions (e.g. 'png,gif', ['png','gif'], 'png')
    :return: True if the file has the extension, false in other cae
    """
    ext_file = getExtension(filepath)

    if type(extensions) is str:
        # remove spaces:
        extensions = extensions.replace(' ', '')
        # split based on commas:
        extensions = extensions.split(',')

    if type(extensions) is not list:
        raise ValueError("checkExtension >> A list or string is expected (e.g. 'png,gif', ['png','gif'], 'png')")

    return ext_file in extensions


def getPathToFile(msg='Please provide the path to the file', type_file='*'):
    """
    Asks for the path of a file.
    :param msg: mesage to be asked to the user. By default: 'Please provide the path to the file'
    :param type_file: type of interest. By default any (*). Provide the list of types using commas.
        e.g. 'png,tif'
    :return: path to the file
    """

    ans = False

    while not ans:
        str = '%s(%s):' % (msg, type_file)
        filepath = input(str)
        # Check if exists
        ans = os.path.isfile(filepath)

        if ans and type_file != '*':
            ans = checkExtension(filepath, type_file)

            if not ans:
                print('   ** File with extension %s not selected' % type_file)
            else:
                print('   Great!! selected file:%s'%filepath)
        else:
            print('    ** File %s not found **' % filepath)

    return filepath


def getPathToFolder(msg='Please provide the path to the folder'):
    """
    Asks for the path of a folder. This method creates the folder if not exists
    :param msg: mesage to be asked to the user. By default: 'Please provide the path to the folder'
    :return: path to the folder
    """
    str = '%s:' % msg
    path_folder = input(str)

    if not os.path.exists(path_folder):
        # create new folder
        os.mkdir(path_folder)
        print('New folder in %s' % path_folder)

    else:
        while os.path.exists(path_folder) and not os.path.isdir(path_folder):
            path_folder = input(str)

    return path_folder


def getCurrentFolderIfNot(folder):
    """
    :param folder: folder
    :return: the current folder if folder not exists, folder in other case
    """
    if folder is None or not os.path.exists(folder):
        # get default folder:
        folder = os.getcwd();

    return folder


def saveDataIntoFile(file_path, data):
    """
    Save data in a file
    :param file_path: file path
    :param data: data to be saved
    :return: the path to the data saved (if any) None in other case
    """

    if os.path.exists(file_path):
        # delete file
        os.remove(file_path)

    try:
        f = open(file_path, 'w')
        f.write(data)
        f.close()
    except:
        print(Fore.RED, end='')
        print('The file cannot be open %s' % file_path)
        print(Style.RESET_ALL, end='')
        return None

    return file_path



def showOptions(options):
    """
    Shows a list of options that must be chosen by the user
    :param options: list of options given as strings e.g. ["Load file", "Analyse file"]. Do not include "Exit" in your
        list, this method will include the option to exit.
    :return: the option chosen as integer (position of the option chosen). Exit = len(option)+1
    """
    # Add Exit option is there is not included
    options = options + ["Exit"]

    print("Choose the action:")
    n = 1
    for o in options:
        str_opt = "[%d]  %s" % (n, o)
        n += 1
        print(str_opt)

    ans = False
    while not ans:
        ans = input("Your answer is: ")
        if not isNumber(ans) or (int(ans) < 1 or int(ans)>=n):
            ans = False

    return int(ans)



def isURL(url):
    """
    https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    :param url: string to be checked
    :return: true if the param url is a URL, false in other case
    """
    if url is None or type(url) is not str or len(url) == 0: return False
    # returns if a URL is a domain
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url)


def suspiciousURL(filepath, apikeyVT = None, threshold = 0, debug=False):
    """
    Checks a list of URL in a file or a direct URL if the input is a URL. When the URL is considered malicious this
    method returns True. False in other case.
    :param file: file with a list of URLs or a single URL
    :param apikeyVT: api key to use VirusTotal
    :param threshold: number of positives to consider the URL malicious (0 by default)
    :param debug: if True then prints the response from the server (False by default)
    :return: if the input is a URL then true or false depending on the threshold, if the
            input is a file, then this method returns a list of malicious URLs.
    """
    # VT params:
    vt_url = 'https://www.virustotal.com/vtapi/v2/url/report'

    if os.path.isfile(filepath):
        eve_urls = []
        with open(filepath, "r") as fp:
            url = fp.readline()
            while url:
                if isURL(url):
                    # ask info about url
                    if apikeyVT is not None:
                        params = {'apikey': apikeyVT, 'resource':url, 'allinfo':True}
                        response = requests.get(vt_url, params=params)
                        if response is not None:
                            try:
                                resjson = response.json()
                                if debug: pprint.pprint(resjson)
                                posit = resjson.get('positives')
                                if posit is not None and int(posit) > threshold:
                                    print('Evi URL: %s, positives:%s' % (url, posit))
                                    eve_urls += [(url, posit, resjson)]
                                else:
                                    if debug: print('URL %s positives: %s, threshold: %s' %
                                                    (url, posit, threshold))
                            except ValueError:
                                print('Error when processing %s ' % url)
                        else:
                            if debug: print('No info for %s' % url)
                else:
                    if debug: print('Not URL: %s' % url)
                url = fp.readline()

        if len(eve_urls)==0: return False
        return eve_urls
    elif isURL(filepath):
        # ask only for this url
        params = {'apikey': apikeyVT, 'resource':filepath, 'allinfo':True}
        response = requests.get(vt_url, params=params)
        if debug: pprint.pprint(response.json())
        return int(response.json()['positives']) > threshold

    return False


def checkDomain(filepath, apikeyVT = None, debug=True):
    """
    Checks a list of domains in a file or a direct domain if the input is a domain
    :param filepath: file with a list of domains or a single domain
    :param apikeyVT: api key to use VirusTotal
    :param debug: if True then prints the response from the server (True by default)
    :return: prints the domain info, if the input is a file then returns an array with the name of the domains that
             exists
    """
    # VT params:
    vt_url = 'https://www.virustotal.com/vtapi/v2/domain/report'

    if os.path.isfile(filepath):
        doms = []
        with open(filepath) as fp:
            domain = fp.readline()
            while domain:
                if apikeyVT is not None:
                    params = {'apikey': apikeyVT, 'domain':domain}
                    response = requests.get(vt_url, params=params)
                    if response is not None:
                        if debug: pprint.pprint(response.json())
                        doms += [domain]
                domain = fp.readline()
        if len(doms) == 0: return False
        return doms
    else:
        # ask only for this domain
        params = {'apikey': apikeyVT, 'domain':filepath}
        response = requests.get(vt_url, params=params)
        if debug: pprint.pprint(response.json())
        return True

    return False

#------------------------------------------------------
#   HASHES
#------------------------------------------------------
ALG = ['MD5', 'SHA256', 'SHA1']

def md5(fname):
    """
    https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    :param fname:
    :return:
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def hash(file, hashtype):
    """
    Calculate the hash
    :param file: file.
    :param hashtype: hash algorithm: MD5, SHA256 or SHA1.
    :return: hash value of file.
    """

    if not os.path.isfile(file) or not isinstance(hashtype, str):
        raise ValueError('hash>> unexpected type - expected file and string for hashing algorithm')

    if hashtype.upper() == 'MD5':
        hasher = hashlib.md5()
    elif hashtype.upper() == 'SHA256':
        hasher = hashlib.sha256()
    elif hashtype.upper() == 'SHA1':
        hasher = hashlib.sha1()

    # Calculate hash for file:
    with open(file, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)

    return hasher.hexdigest()


def checkhash(file, hashchosen, hashtype, printme=False):
    """
    Check if a file has a hash.
    :param file: file to be proved.
    :param hashchosen: hash to be compared.
    :param hashtype: hash algorithm: MD5, SHA256 or SHA1.
    :param printme: print the output, False by default
    :return: True if the hashtype(file) == hash, False in other case.
    """
    if not isinstance(hashchosen, str) or not isinstance(file, str) or not isinstance(hashtype, str):
        raise ValueError('checkhash>> unexpected type for input values - expected str')

    # Calculate:
    hashfile = hash(file, hashtype)

    # Say result
    if printme: print('Input hash:%s' % hashchosen)
    if printme: print('Hash %s for %s: %s' % (hashtype, file, hashfile))

    # True if these are equal, false in other case
    return str(hashfile).upper() == hashchosen.upper()


#------------------------------------------------------
#   SIGNATURE
#------------------------------------------------------
def checksignature(file, extension, printme=False):
    """
    Checks if the file signature matches with the extension chosen
    :param file: file to be checked.
    :param extension: extension chosen.
    :return: True if type(file) == extension, the type is calculated based on the signature of the file
    :Refs: https://0x00sec.org/t/get-file-signature-with-python/931
    """
    #remove '.' from extension if exists
    if extension[0]=='.': extension = extension[1:]

    signature.compile_sigs()
    results = signature.check_sig(file) # [(sig, desc, offset), (sig, desc, offset), ... etc.]

    if results:
        # find longest signature, and desc for output formatting purposes
        big_sig = len(max([i[0] for i in results], key=lambda x: len(x)))
        big_desc = len(max([i[1] for i in results], key=lambda x: len(x)))

        if printme: print("\n[*] First candidate signature:\n")
        sig, desc, offset = results[0][0], results[0][1], results[0][2]
        s = ("[+] {0:<%ds} : {1:<%d} {2:<20s}" % (big_sig, big_desc)).format(sig, desc, "<- Offset: " + str(offset))
        if printme: print(s)

        return extension.upper() in desc
    else:
        print('No tmp for signatures')

    return False


#------------------------------------------------------
#   METADATA
#------------------------------------------------------

def getMeta(file):
    """
    Returns metadata of a file.
    :param file:
    :return:
    """
    if not os.path.isfile(file): return {}

    #use exiftool to get metadata:
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(file)   #_batch([file])

    if metadata is not None and len(metadata)>0:
        return metadata

    return {}


def isMetadata(meta, value, file):
    """
    Checks if a pair meta:value is included as metadata in file.
    :param meta: data.
    :param value: value.
    :param file: file.
    :return: True if the pair meta:value is included, False in other case.
    """
    metadata = getMeta(file)

    return meta in list(metadata.keys()) and metadata[meta]==value


def setMeta(file, meta, value):
    """
    Changes metadata (if meta exists) or adds a new one, meta:value
    :param file: file to be processed.
    :param meta: name of the field to be included as metadata.
    :param value: value for the field meta
    :return: file with the metadata modified/added.
    """

    if not os.path.isfile(file): return False

    # use exiftool to modify metadata:
    meta = '-%s="%s"' % (meta, value)

    with exiftool.ExifTool() as et:
        params = map(os.fsencode, ['-File:%s=%s' % (meta, value), '%s' % file])
        et.execute_json(*params)#meta, file)

    return isMetadata(meta, value, file)


# ------------------------------
#       FILES
# ------------------------------

def getListOfFiles(directory):
    """
    :param directory: folder to be processed
    :return: dictionary with information about the files in the directory
    """

    files = {}

    for root, dirs, files in os.walk(directory):
        for filename in files:
            myfile = File(filename,root)
            files.update({file:{'name':filename,'root':root,'filepath':myfile.getPath()}})

    return files


# ------------------------------
#       MAIN METHOD
# ------------------------------
if __name__ == "__main__":
    """
    Example: python3 auxiliar.py 
             2
             /Users/nieto/Documents/CHALLENGES/ATENEA/FORENSE/Castelvania/domains.txt
    """
    options = ["Check URL", "Check URL (file)", "Check domain"]
    max_options = len(options)

    # Show options:
    ans = showOptions(options)

    while ans <= max_options:

        if ans == 1: # Check url
            url = ''
            while not isURL(url):
                url = input('Please, provide a URL:')
            if suspiciousURL(url, apikeyVT='8c0b75acc0a67e62617b6ddd631e5ca5c9e24e612eb3562ad3e41a9bed446ca1', debug=False):
                print('URL not clean!!!')
            else:
                print('URL clean: means that the number of positives returned by VT is less than threshold (0 by default)')

        elif ans == 2: # Check url (file)
            file = getPathToFile(msg='Please, provide a valid file with a list of URLs:',type_file='txt')
            res = suspiciousURL(file, apikeyVT='8c0b75acc0a67e62617b6ddd631e5ca5c9e24e612eb3562ad3e41a9bed446ca1', debug=False)
            if type(res) is list:
                for r in res:
                    print(r[0])
                input('Press enter to see details')
                for r in res:
                    print('---------------------------------------------')
                    print("URL:%s:" % r[0])
                    print("Positives:%s, JSON Details:" % r[1])
                    pprint.pprint(r[2])
                    input('continue...')
            else:
                print('All URLs are trustworthy')

        elif ans == 3: # Check domain
            domain = input('Please, provide a domain:')
            checkDomain(domain, apikeyVT='8c0b75acc0a67e62617b6ddd631e5ca5c9e24e612eb3562ad3e41a9bed446ca1', debug=True)

        input("Press enter to continue...")
        ans = showOptions(options)


####################################
#       database methods
####################################

def createDatabase(dbname, username, password, host="localhost"):
    """
    :param dbname: name of the database
    :param username: DB's user's name
    :param password: user's pwd
    :param host: host (e.g. localhost)
    :return: this method creates the database
    """
    mydb = mysql.connector.connect(host=host, user=username, password=password)
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE %s" % dbname )


def createTable(dbname, username, password, tbname,
                   params="name VARCHAR(255), path VARCHAR(255)", id="id INT AUTO_INCREMENT", host="localhost"):
    """
    :param dbname: name of the database - this must be created before call this method
    :param username: DB's user's name
    :param password: user's pwd
    :param tbname: name of the new table for the DB
    :param params: string with the params for the table: name VARCHAR(255), address VARCHAR(255)
    :param id: key for the table - id INT AUTO_INCREMENT by default
    :param host: host (e.g. localhost)
    :return: this method creates a new table in the DB
    """
    mydb = mysql.connector.connect(host=host, user=username, password=password, database=dbname)
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE %s (%s)" % (tbname, params))

    return True


class ScrollbarFrame(Frame):
    """
    source: https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
    Extends class tk.Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard tk.Frame
    """
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        vsb = Scrollbar(self, orient="vertical")
        vsb.pack(side=RIGHT, fill=Y)
        vsb2 = Scrollbar(self, orient="horizontal")
        vsb2.pack(side=BOTTOM, fill=X)

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=vsb2.set)
        vsb2.configure(command=self.canvas.xview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = Frame(self.canvas, background=self.canvas.cget('bg'))
        self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))