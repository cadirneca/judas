
import os
import re
import json
from pprint import pprint
import os.path
from colorama import init, Fore, Back, Style
import imagemounter as imm

#------------------------------------------
#       DIRECTORY ANALYSIS
#------------------------------------------
def directoryAnalysis (casedirectory,words,ignore):

    if(len(ignore)>0):
        print("Searching IPs in Directory %s..." % (casedirectory))

    rx = re.compile('|'.join(words))

    for root, dirs, files in os.walk(casedirectory):

       for filename in files:
           #try:
                if filename != '.DS_Store':
                    filepath = "%s/%s" % (root,filename)
                    print("-- Searching in %s ..." % (filepath))
                    with open(filepath, 'r') as df:
                        data = df.read()
                    for match in rx.finditer(data):
                        # Use the MatchObject as you like
                        print(match.span())
                else:
                    print("xx %s ommited ..." % (filename))
           #except Exception:
               # print("Unexpected error:", sys.exc_info()[0])
               # pass


#------------------------------------------
#       JSON ANALYSIS
#------------------------------------------

def dataFromJson (pathtofile):
    "Read json file in a path"
    data = {}
    extension = os.path.splitext(pathtofile)[1]
    if extension == '.json':
        with open(pathtofile) as df:
            data = json.load(df)
            df.close()

    return data


def printJson (words, pathtofiles):
   "Read json files in a path"
   print("Searching in JSON files in directory %s..." % (pathtofiles))

   rx = re.compile('|'.join(words))
   for root, dirs, files in os.walk(pathtofiles):
       for filename in files:
           filepath = "%s/%s" % (root, filename)
           data = dataFromJson(filepath)
           if(data): pprint(data)

def isRelevant(k, words):
    "Check if a part of k match with any word"
    for w in words:
        print("key:%s, word:%s" % (k, w))
        if((k.find(w)!=-1) or (w.find(k)!=-1)): return True
    return False

def getID(dictionary):
    "Return the ID in a dictionary based on a set of recognised IDs"

    IDs = ['serialNumber', 'SerialNumber', 'identificator', 'ID', 'Id']
    keys = dictionary.keys()
    rel_ids = {}
    for k in keys:
        if (isRelevant(k, IDs)):
            rel_ids.update({k:dictionary.get(k)})
    return rel_ids


def eatJson(data, words, info):
    "Returns a structure with information about words of interest"

    if (len(info) == 0):
        info = {}
        for w in words:
            info.update({w:{}})

    for k in data:
        if(isRelevant(k, words)):
            # is a word of interest that is in our dictionary
            infowords = info.get(k)
            # infowords is a dictionary with elements of a type
            # each element in infowords is a different element of a type
            # e.g. if k=='device', then infowords={{
            values = data.get(k) #e.g. all info in data about the key
            if (isinstance(values, dict)):
                # have a dictionary
                idlist = getID(values)
                # the dictionary is relevant for (at least) a type of word
                if(len(id)>0): #key(s) for id founded
                    for i in idlist:
                        # add the dictionary to each element
                        infowords.cannibalism({i:values})
            info.update({k:infowords})

    return info


def eatJsonDirectory (words, pathtofiles):
    "Extract relevant information from json files"

    print("Analysing in JSON files in directory: %s..." % (pathtofiles))
    info = {}

    for root, dirs, files in os.walk(pathtofiles):
        for filename in files:
            filepath = "%s/%s" % (root, filename)
            data = dataFromJson(filepath)

            info = eatJson(data, words, info)

    print("Results for:", words)
    print(info)


def writeJson(root, filename , outputfile, action):

    "Append ('a') or Write ('w') a json in an output file"
    filepath = "%s/%s" % (root, filename)

    data = dataFromJson(filepath)
    extension = os.path.splitext(filepath)[1]
    if extension == '.json':
        with open(outputfile, action) as out:
            #print(Fore.GREEN, file=out, end='')
            print("--------------------------------", file=out)
            print("%s:" % (filename), file=out)
            print("--------------------------------", file=out)
            #print(Style.RESET_ALL, file=out, end='')

            pprint(data, stream=out)

def writeJsonDirectory (pathtofiles, outputfile):

    "Saving information from JSON files in a file"

    logfile = "~/PycharmProjects/DFRWS/%s" % (outputfile)

    if(os.path.isfile(logfile)):
        os.remove(logfile)

    for root, dirs, files in os.walk(pathtofiles):

        for filename in files:
            writeJson(root,filename,outputfile,'a')


def changeColorFor(word,str,color):
    start_index = str.find(word)
    first = 0
    while(start_index!=-1):
        end_index = start_index + len(word)

        print(str[first:start_index], end='')
        print(color, end='')
        print(str[start_index:end_index], end='')
        print(Style.RESET_ALL, end='')

        # check if there are more appearances in the same string
        start_index = str.find(word, start_index + 1)
        if(start_index==-1):
            print(str[end_index:]) # end string
        else:
            first = end_index



def searchInDirJson(words, path, filelog='alljson.txt'):
    "Search in a directory of jsons a list of words"

    strlog = 'Searching keywords:%s in %s\n' % (words, path)
    fileslist = ''
    if(len(filelog)>0):
        #prepare file log
        logfile = "./%s" % (filelog) #"~/PycharmProjects/DFRWS/%s" % (filelog)

        if (os.path.isfile(logfile)):
            os.remove(logfile)

    wcount = 0
    for root, dirs, files in os.walk(path):

        for filename in files:
            filepath = "%s/%s" % (root,filename)
            data = dataFromJson(filepath)
            found = False
            for w in words:
                str = json.dumps(data)
                if(str.find(w)!=-1):
                    wcount += 1
                    if(not found):
                        print(Fore.GREEN)
                        print("- Occurences in file %s ..." % (filename))
                        strlog = "%s   - Occurences in file %s ...\n" % (strlog, filename)
                        print(Style.RESET_ALL)
                        found = True
                        if fileslist.find(filename)==-1:
                            fileslist += "->"+filename +"\n"

                        if(len(filelog)>0):
                            writeJson(root, filename, filelog, 'a')

                    #change the color of the word in the string
                    changeColorFor(w, str, Fore.RED)

                    strlog = "%s        %s \n" % (strlog, str)
    print("** Number of detections: %d for words:%s in %s" % (wcount, words, path))
    strlog = "%s** Number of detections: %d for words:%s in %s\n" % (strlog, wcount, words, path)

    return {'files':fileslist, 'summary':strlog}



#------------------------------------------
#       IMAGE ANALYSIS
#------------------------------------------
def analyseimage(pathtoimg):
    # mount the image
    parser = imm.ImageParser(pathtoimg)
    print(parser)
    print(parser.fstypes)

    #for v in parser.init():
    #    print(v.size)
    #root = parser.reconstruct()
    #print(root.mountpoint)
    #parser.clean()

