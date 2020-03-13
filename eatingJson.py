######
# @author:      Ana Nieto,
# @email:       nieto@lcc.uma.es
# @institution: University of Malaga
# @country:     Spain
# @website:     https://www.linkedin.com/in/ana-nieto-72b17718/
######

import json
import re
from abc import ABCMeta, abstractmethod
import datetime
from colorama import Fore, Style
import os
import pygraphviz as pgv  # dot files
import networkx as nx
from networkx.readwrite import json_graph
import base64
import warnings
import pprint
import ntpath
import http_server
import numpy as np
import matplotlib
matplotlib.use("TkAgg") # this is for Mac OS
from matplotlib import pyplot as plt

import sys


####################################
#           CLASS ANYTHING
####################################
class Anything(metaclass=ABCMeta):

    #CONTEXT = Context.Context()  # unique context

    # Special Keys - Anything childs
    SUP_USERS_KEY = 'User(id)'
    SUP_DEVICES_KEY = 'Device(id)'
    SUP_ADDRESS_KEY = 'Address(id)'
    SUP_CARDS_KEY = 'Card(id)'
    SUP_ROUTE_KEY = 'Route(id)'
    SUP_SERVICE_KEY = 'Service(id)'
    SUP_ACTIVITY_KEY = 'Activity(id)'
    SUP_ACTION_KEY = 'Action(id)'
    # Other Keys:
    OBJECTS_TO_PROCESS = 'Objects(Anything)'
    FILES_KEY = 'Files'
    LABELS_KEY = 'Label'
    TYPES_KEY = 'Type'
    UNAME_KEY = 'UName'
    PCODE_KEY = 'PostalCode'
    COUNTRYCOD_KEY = 'Country(code)'
    TIMEZONE_KEY = 'Timezone'
    TIMESTAMP_KEY = 'Timestamp'
    IP = 'IP'
    # TYPES:
    TYPES = [SUP_USERS_KEY, SUP_DEVICES_KEY, SUP_ADDRESS_KEY, SUP_CARDS_KEY, SUP_ROUTE_KEY, SUP_SERVICE_KEY,
             SUP_ACTIVITY_KEY, SUP_ACTION_KEY]

    # For backpack:
    BACKPACK_DEFAULT_KEYS = [FILES_KEY, SUP_USERS_KEY, SUP_DEVICES_KEY, SUP_ADDRESS_KEY, SUP_CARDS_KEY, SUP_ROUTE_KEY,
                             SUP_SERVICE_KEY, SUP_ACTIVITY_KEY, SUP_ACTION_KEY, OBJECTS_TO_PROCESS]

    # For equivalences:
    EQUIVALENCES = {FILES_KEY: ['files'],
                    LABELS_KEY: ['label'],
                    SUP_ADDRESS_KEY: [SUP_ADDRESS_KEY, 'address'],
                    SUP_DEVICES_KEY: [SUP_DEVICES_KEY, 'device', 'sourceDevice', 'deviceSerialNumber',
                                      'deviceId', 'serialNumber'],
                    SUP_USERS_KEY: [SUP_USERS_KEY, 'user', 'customerId', 'searchCustomerId', 'registeredCustomerId',
                                    'registeredUserId', 'deviceOwnerCustomerId'],
                    SUP_CARDS_KEY: [SUP_CARDS_KEY, 'card'],
                    SUP_ROUTE_KEY: [SUP_ROUTE_KEY, 'route'],
                    SUP_SERVICE_KEY: [SUP_SERVICE_KEY, 'service'],
                    SUP_ACTIVITY_KEY: [SUP_ACTIVITY_KEY, 'activity'],
                    SUP_ACTION_KEY: [SUP_ACTION_KEY, 'action'],
                    TYPES_KEY: ['type', 'cardType', 'itemType'],
                    UNAME_KEY: ['username'],
                    PCODE_KEY: ['postalCode', 'postal', 'Zipcode'],
                    COUNTRYCOD_KEY: ['countryCode'],
                    TIMEZONE_KEY: ['timezone', 'timeZoneId', 'timeZoneRegion'],
                    TIMESTAMP_KEY: ['timestamp', 'creationTimestamp'],
                    IP: ['IP']}
    # This is to maintain some statistics about the objects created...
    STATISTICS = {"Total":0,
                  "User":{"number":0, "dicto":{}},
                  "Device":{"number":0, "dicto":{}},
                  "Address":{"number":0, "dicto":{}},
                  "Card":{"number":0, "dicto":{}},
                  "Route":{"number":0, "dicto":{}},
                  "Service":{"number":0, "dicto":{}},
                  "Activity":{"number":0, "dicto":{}},
                  "Action":{"number":0, "dicto":{}},}


    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, id, others=None, notlistable=[OBJECTS_TO_PROCESS], statistics=True):
        if id is None:
            raise ValueError('Unexpected value for "id", the identificator cannot be None')
        self.id = id
        self.history = ''
        self.plotHistory = True
        self.container = None # to be used if the node is printed in a graph

        if others is None:
            self.initBackpack()
        else:
            # combine backpack with the default backpack
            self.initBackpack(others)

        if notlistable is None:
            self.notlistable = [self.OBJECTS_TO_PROCESS]
        else:
            self.notlistable = notlistable
            self.addNotListable(self.OBJECTS_TO_PROCESS)

        self.addHistory('Object created with values:%s\n' % self.printInLine())

        if statistics:
            key = self.__class__.__name__
            values = Anything.STATISTICS.get(key)
            number = values.get("number")
            dicto = values.get("dicto")
            check = dicto.get(id)

            if check is None:
                # new term
                dicto.update({id:1})
            else:
                # item exists:
                dicto[id] = dicto[id] + 1

            #update:
            Anything.STATISTICS["Total"] = Anything.STATISTICS["Total"] + 1
            Anything.STATISTICS[key] = {"number":number+1, "dicto":dicto}


    def initBackpack(self, seed=None):
        """
        :return: the backpack by default
        """
        #self.backpack = dict.fromkeys(Anything.BACKPACK_DEFAULT_KEYS, [])
        self.backpack = {Anything.FILES_KEY:[], Anything.SUP_USERS_KEY:[], Anything.SUP_DEVICES_KEY:[],
                         Anything.SUP_ADDRESS_KEY:[], Anything.SUP_CARDS_KEY:[],
                            Anything.SUP_ROUTE_KEY:[], Anything.SUP_SERVICE_KEY:[], Anything.SUP_ACTIVITY_KEY:[],
                            Anything.SUP_ACTION_KEY:[], Anything.OBJECTS_TO_PROCESS:[]}
        self.addHistory('Backpack initialised... ')

        if seed is not None and len(seed)>0:
            # add seeds to the backpack:
            for s in seed:
                self.backpack.update({s:seed.get(s)})

        return True

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    def __del__(self):
        #print("%s's object %s died." % (self.__class__.__name__,self.id))
        None

    #----------------------------------
    #       METHODS TO GET THE CONTEXT
    #----------------------------------

    #def getContext(self):
        """
        This method is to consult the structure Context of the Class
        :return: the context - unique of the class
        """
    #    return Anything.CONTEXT

    #----------------------------------
    #       ABSTRACT METHODS
    #----------------------------------

    @abstractmethod
    def eatAddress(self, object):
        pass

    @abstractmethod
    def eatRoute(self, object):
        pass

    @abstractmethod
    def eatService(self, object):
        pass

    @abstractmethod
    def eatUser(self, object):
        pass

    @abstractmethod
    def eatDevice(self, object):
        pass

    @abstractmethod
    def eatCard(self, object):
        pass

    @abstractmethod
    def eatAction(self, object):
        pass

    @abstractmethod
    def eatActivity(self, object):
        pass

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getContainer(self):
        """
        :return: A container to be used in a graph
        """
        if self.container is None:
            self.container = Container(self.getIdGraph())
            self.container.setLabel(self.getId())
            # Add this info in the object to be shown
            self.putInBackpack('ContainerID(Web Graph)', self.container.getID())

        return self.container

    def isType(self, key):
        """
        This method allows to check if a key correspond to one of the basic types (e.g. User)
        :return: True if the key is one of the basic types, False in other case
        """
        return key in Anything.TYPES

    def getId(self):
        """
        :return: identificator (id) of this object
        """
        return self.id

    def getNotListable(self):
        """
        To check the elements in the backpack that are not listable
        :return: list of keys that are not listable
        """
        return self.notlistable

    def isBlackKey(self, blackkey):
        """
        To check if a key is a blackkey (not listable)
        :param blackkey: key to be ckecked
        :return: Ture if the key is a blackkey, false in other case
        """
        return blackkey in self.getNotListable()

    def getHistory(self):
        """
        :return: the history of changes in the object
        """
        return self.history

    def getSearchTerms(self):
        """
        :return: list with keys that can be used to search the items in the context of the object
        """
        "Returns the keys that can be used in searches"
        return self.EQUIVALENCES.keys()

    def getIdGraph(self):
        """
        :return: ID that is used by default to describe the object in a graph
        """
        return "%s(id):%s" % (self.__class__.__name__, self.getId())


    def getEquivalence(self, key, update=True):
        """
        This method is for get the key to be used for get/include items in the backpack; a key can be represented in
        multiple ways in this context, so this method operates such as translator
        :param key: key that want to be used for search a term
        :param update: if True (by default) updates the structure of EQUIVALENCES with 'key' if not included. If False
        then returns None in case there is not a pre-defined equivalence
        :return: the equivalence of the term to perform the search. Use the word returned in order to search for a
        item in this object and/or update the context of this object.
        """
        if key is None:
            warnings.warn("getEquivalence>> Unexpected 'key' value, please use a string as key value")
            return None

        for k in Anything.EQUIVALENCES:
            val = Anything.EQUIVALENCES.get(k)
            #print("getEquivalence>>candidate:%s, key analysed:%s, values:%s" % (key, k, [x.lower() for x in val]))
            if key.lower() in [x.lower() for x in val]:
                #print(Fore.GREEN)
                #print("return:%s" % k)
                #print(Style.RESET_ALL)
                return k

        # Else, is a new term
        if update:
            Anything.EQUIVALENCES.update({key:[key]})
            return key

        return None

    def getBackpack(self, key=None):
        """
        :param key: if None (by default) returns all the values in backpack. In other case, this returns the values in
        the backpack given the specific key value.
        :return: List of items in the backpack. If there are not items, then this method returns an empty list [].
        """
        if key is None:
            values = list(self.backpack.values())
            values = list(set([o for v in values for o in v])) #set is to remove duplicates

        else:
            values = self.backpack.get(self.getEquivalence(key))
            if values is None: values = []
        return values

    def getObjectsForProcessing(self, idlist=None, key=None, remove=True):
        """
        This method allows the access to the objects to be processed
        :param key: if provided, only returns objects with a specific type (e.g. User)
        :param remove: if True (by default) deletes the objects returned after this method is called
        :return: a list of objects to be processed
        """
        if key is not None and not Context.isType(key):
            warnings.warn("getOjects>> Unexpected 'key' value, please provide one of the main Types (e.g. User)")
            return []
        returned = []
        tbp = self.getBackpack(Anything.OBJECTS_TO_PROCESS)

        if key is not None:
            tbp = [x for x in tbp if x.__class__.__name__ == key]
        if idlist is not None and len(idlist)>0:
            tbp = [x for x in tbp if x.getId() in idlist]
        returned = tbp

        # Add to these objects info about his parent:
        rf = self.getRelatedFiles()
        for r in returned:
            r.addRelatedFiles(rf)
            r.eat(self)

        if remove:
            all = self.getBackpack(Anything.OBJECTS_TO_PROCESS)
            not_returned = [x for x in all if x not in returned]
            self.backpack.update({Anything.OBJECTS_TO_PROCESS:not_returned})

        return returned

    def getRelatedIDs(self):
        """
        This method returns all the IDs for objects that are related with this object
        :return: list of strings, where the strings are identifiers for the objects
        """
        id = list(set(self.getBackpack(Anything.SUP_ADDRESS_KEY) + self.getBackpack(Anything.SUP_DEVICES_KEY)+ \
                self.getBackpack(Anything.SUP_USERS_KEY) +  self.getBackpack(Anything.SUP_ACTIVITY_KEY)+ \
                self.getBackpack(Anything.SUP_ACTION_KEY) + self.getBackpack(Anything.SUP_CARDS_KEY)+ \
                self.getBackpack(Anything.SUP_SERVICE_KEY) + self.getBackpack(Anything.SUP_ROUTE_KEY)))
        return id

    def getKeys(self):
        """
        :return: a list of keywords to access to the backpack
        """
        keys = self.backpack.keys()
        return list(keys)

    def getRelatedFiles(self):
        """
        This method helps to consult the related files of this object
        :return: A list of related files of the object
        """
        return self.getBackpack(self.FILES_KEY)

    def isKey(self, key):
        """
        This method can be used to check if a key can be used to get a value from the backpack. Unlike 'getEquivalence',
        this method allows the comparation without including the 'key' in the backpack structure
        :param key: key to be checked
        :return: True if the key is defined in the structure in some way (either dirctly or indireclty as equivalence),
        false in other case
        """
        return self.getEquivalence(key, update=False) is not None

    def inBackpack(self, value):
        """
        This method can be used to check if a value is in the backpack
        :param object: object to be checked
        :return: The keys where the object is included, empty list in other case
        """
        keys = self.getKeys()
        return [k for k in keys if value in self.getBackpack(k)]


    def printInLine(self, line=True):
        """
        This method formats this object for its comprehension in a string
        :param line: True (default) if we want the description of the object in a single line. If False, then the
        character '\n' is introduced
        :return: a String with the description of the object
        """
        lin = ""
        if not line: lin = "\n"

        str = "id: %s%s" % (self.getId(), lin)

        for k in self.getKeys():
            if k not in self.getNotListable():
                item = self.getBackpack(k)
                if len(item)>0:
                    str = "%s%s: " % (str, k)
                    for i in item:
                        # format item in backpack:
                        if isinstance(i, Anything):
                            str = "%s%s, " % (str, i.getId())
                        else:
                            str = "%s%s, " % (str, i)
                    str = str[0:len(str) - 1]
                    str += lin

        if self.plotHistory:
            str = "%s%s%s" % (str, self.getHistory(),lin)

        return str

    @staticmethod
    def autolabel(rects, ax):
        """
        Taken from: http://sparkandshine.net/en/draw-with-matplotlib-stacked-bar-charts-with-error-bar/
        """
        # write the value inside each bar
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., height - 0.4,
                    '%d' % int(height), fontsize=9, ha='center', va='bottom')

    @staticmethod
    def plotGraph(means_frank, means_guido, label_frank, label_guido, x_label, y_label, title, bar_groups):
        """
        Adapted from: https://pythonspot.com/matplotlib-bar-chart/ and
        http://sparkandshine.net/en/draw-with-matplotlib-stacked-bar-charts-with-error-bar/
        This method plots a graph, bar-chart, two columns each group
        :param means_frank: set of values for the first bar
        :param means_guido: set of values for the second bar
        :param label_frank: label for the legend (first bar)
        :param label_guido: label for the legend (sedond bar)
        :param x_label: label for the x-axes in the graph
        :param y_label: label for the y-axes in the graph
        :param title: title for the plot
        :param bar_groups: name of the groups
        :return: this method prints a graph with the values given as parameters
        """
        fig, ax = plt.subplots()
        n_groups = len(bar_groups)
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.8

        rects1 = plt.bar(index, means_frank, bar_width,
                         alpha=opacity,
                         color='b',
                         label=label_frank)

        rects2 = plt.bar(index + bar_width, means_guido, bar_width,
                         alpha=opacity,
                         color='g',
                         label=label_guido)

        Anything.autolabel(rects1, ax)
        Anything.autolabel(rects2, ax)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(index + bar_width, bar_groups)
        plt.legend()

        plt.tight_layout()
        plt.show()

    @staticmethod
    def printStatistics(printDicto=True, graph=True):
        """
        Print statistics about the number of objects generated, the class of the object etc.
        :param printDicto: if True (default) prints in the terminal the dictionary as it is
        :return: dictionary with the statistics and the summary in form of string
        """
        statistics = ""
        if printDicto: pprint.pprint(Anything.STATISTICS)

        statistics = "Number of objects generated (total):%d\n" % Anything.STATISTICS.get("Total")
        keys = list(Anything.STATISTICS.keys())
        keys.remove("Total")
        total_inst_class = ()
        unique_obj_class = ()
        class_name = ()
        for k in keys:
            # Values:
            values = Anything.STATISTICS.get(k)
            dicto = values.get("dicto")
            total = values.get("number")
            num_objects = len(dicto.keys())
            promed = total / num_objects
            # Statistics for the class:
            statistics = "%s* %s class, number of instances (total):%d, different objects:%d, " \
                         "average:%d per object\n" % (statistics, k, total, num_objects, promed)
            total_inst_class = total_inst_class + (total,)
            unique_obj_class = unique_obj_class + (num_objects,)
            class_name = class_name + (k, )
            # for each object in the class:
            for ki in dicto.keys():
                statistics = "%s   ->%s:%d\n" % (statistics, ki, dicto.get(ki))

        #print in a graph
        if graph:
            Anything.plotGraph(total_inst_class, unique_obj_class, '# Created (total)', '# Used (unique identifier)', 'Class', 'Number of instances',
                           'Number of instances by class', class_name)

        return {'order': class_name, 'total':total_inst_class, 'unique':unique_obj_class, 'summary':statistics}

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def putInBackpack(self, key, inputValue, replace=True, eat=False):
        """
        This method puts a value in the backpack
        :param key: key in where the value will be added
        :param inputValue: value to be added
        :param replace: if True (by default) replace the value if exists
        :param eat: if False (default) the value is not consumed. Only for values of type Anything. If eat==True, then
        replace becomes False by default (because the object is eaten)
        :return: True if the value was added to the backpack, False in other case
        """
        if key is None or inputValue is None:
            msg = "putInBackpack>> Unexpected input values key:%s, value:%s" % (key, inputValue)
            warnings.warn(msg)
            return False
        if eat: replace=False

        key = self.getEquivalence(key) #get the equivalence
        values = self.getBackpack(key) # values for this key in the backpack
        #print("key:%s, values:%s, inputvalues:%s" % (key, values, inputValue))
        if inputValue not in values:
            # new value to be added to the list:
            values.append(inputValue)
        else:
            # this value already exists in the backpack:
            index = values.index(inputValue)
            if eat and isinstance(inputValue, Anything):
                values[index].eat(inputValue)
            elif replace:
                values[index] = inputValue

        #print('key:%s, values:%s' % (key, values))
        self.backpack.update({key: values})

        updated = inputValue in self.getBackpack(key)

        return updated


    def addNotListable(self, blackkey):
        """
        Adds a key that will be not listable as parameter in the object
        :param blackkey: key that not will be listed in a print
        :return: True if was added, False in other case (perhaps because the blackkey already exists in the list
        """
        if blackkey is None or not isinstance(blackkey, str):
            warnings.warn("addNotListable>> Unexpected input values, please read the description of the method first")
            return False

        if blackkey not in self.getNotListable():
            self.notlistable.append(blackkey)
            return True

        return False

    def addHistory(self, log):
        """
        This method adds a line to the history of this object
        :param log: a string to be added to the history of this object
        :return: True if the log was added to the history. False in other case
        """

        if not isinstance(log, str):
            warnings.warn("addHistory>> Unexpected 'log' value, logs must be strings!!")
            return False

        self.history = "%s%s>>%s\n" % (self.history, datetime.datetime.today().time().isoformat(), log)
        return True

    def addRelatedFiles(self, fileName):
        """
        This method adds a new file related with this device (e.g. log in where it is mentioned)
        :param fileName: name of the file to be added to the list. If a list is provided, then the list is processed to
        include all the files in the structure
        :return: True if the object was included, False in other case
        """

        if fileName is None:
            warnings.warn("addRelatedFiles>> Unexpected 'fileName' value, fileName must be a string")

        elif isinstance(fileName, list):
            ret = False
            for file in fileName:
                ret = ret or self.putInBackpack(self.FILES_KEY, file)
            return ret
        else:
            return self.putInBackpack(self.FILES_KEY, fileName)



    # ---------------------------------
    #       COMBINE INFORMATION
    # ---------------------------------
    def isRelatedWith(self, object):
        """
        This method helps to decide if the object is related in some way with this object
        :param object: the object to be checked
        :return: True if the object is related with this object (based in our own criteria), False in other case
        """
        return isinstance(object, Anything) and (
                self.__eq__(object) or
                self.inBackpack(object.getId()) or
                object.inBackpack(self.getId()))


    def isGoodEat(self, object, other=None):
        """
        Decides if the object is good for eat based on a set of general criteria
        :param object: the object from which the new data will be extracted
        :param other: other parameters to be considered (None by default)
        :return: True if the object can be eaten, False in other case
        """
        return object is not None and isinstance(object, Anything) and (self.__eq__(object) or self.isReatedWith(object))

    def eatSame(self, object, destroyIfsame=False):
        """
        This method eat an object if is equal to this object
        :param object: the object to be eaten
        :param destroyIfsame: if False (default) the object received is not destroyed after the lunch. In other case,
        the object is destroyed
        :return: True if the object has been eaten, False in other case
        """
        if object is None or not self.__eq__(object):
            warnings.warn("eatSame (%s)>> Unexpected input values, please read the description of the method first,"
                             "or try 'eat' instead." % (self.__class__.__name__s))
            return False

        # combine backpacks:
        keys2 = object.getKeys()
        eat = False
        for k in keys2:
            values = self.getBackpack(k)
            values2 = object.getBackpack(k)
            for v in values2:
                if v not in values:
                    values.append(v)
            #newVal = list(set(values + values2)) #list(itertools.chain.from_iterable([values, values2])) #
            # Update:
            self.backpack.update({k:values})

        # Destroy the last object
        if destroyIfsame: object.__del__()

        return eat

    def eat(self, object, destroyIfsame=False):
        """
        Eats the information from any object. If the object is the same it will be destroyed (by default)
        :param object: object from which the new data will be extracted
        :param destroyIfsame: if False (default) destroys the object received as parameter, True in other case
        :return: True if the object has been eaten, False in other case
        """

        if not isinstance(object, Anything):
            warnings.warn("eat>> Unexpected input values, please read the description of the method firs")
            return None

        if not self.isRelatedWith(object):
            return False

        oc = object.__class__.__name__
        oid = object.getId()
        eaten = False
        if isinstance(object, Address): eaten = self.eatAddress(object)
        elif isinstance(object, Route): eaten = self.eatRoute(object)
        elif isinstance(object, Service): eaten = self.eatService(object)
        elif isinstance(object, User): eaten = self.eatUser(object)
        elif isinstance(object, Device): eaten = self.eatDevice(object)
        elif isinstance(object, Card): eaten = self.eatCard(object)
        elif isinstance(object, Action): eaten = self.eatAction(object)
        elif isinstance(object, Activity): eaten = self.eatActivity(object)
        else:
            warnings.warn("eat>> This method is not able to handle the type of Anything object, please update")
            return False

        if eaten:
            # check the backpack in case oid is not my own id
            if self.getId()!=oid and not self.inBackpack(oid):
                # left a trace (only for objects different from my)
                self.addHistory('Eaten object type %s, id:%s' % (oc, oid))
                self.putInBackpack(oc, oid, eat=True)

        if destroyIfsame: object.__del__()

        return eaten

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        return self.printInLine(False)

    # def __cmp__(self, other): --> no used in python3
    def __cmp__(self, other):
        if isinstance(other, Anything):
            if (self.getId()==other.getId()):
                return 0
            elif (self.getId()<other.getId()):
                return -1
            else:
                return 1
        return None

    def __lt__(self, other):
        return self.__cmp__(other) < 0


    def __eq__(self, other):
        if isinstance(other, Anything):
            return (self.getId() == other.getId())

        return False

    def __hash__(self):
        return self.getId().__hash__()


####################################
#           CLASS ADDRESS
####################################
class Address(Anything):

    ADDRESS = 'Address'
    CITY = 'City'
    COUNTRY = 'Country'
    LABEL = 'Label'
    PLACE_ID = 'PlaceId'
    SETTINGS = 'Settings'
    STATE = 'State'
    STATION = 'Station'
    STREET = 'Street'
    ZIPCODE = 'Zipcode'
    TIMEZONE = 'Timezone'
    IP = 'IP'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, id, addressLine1='', addressLine2='', addressLine3='', city='', countryCode='',
                 country='', label='', placeId=None, settings=None, state=None, stationName=None, street=None,
                 zipcode=None):

        self.id = id

        self.others = {self.ADDRESS:None, self.CITY:None, self.COUNTRY:None, self.LABEL:None, self.PLACE_ID:None,
                       self.SETTINGS:None, self.STATE:None, self.STATION:None, self.STREET:None, self.ZIPCODE:None}

        super().__init__(id, self.others)

        self.putInBackpack('AddressLine1', addressLine1)
        self.putInBackpack('AddressLine2', addressLine2)
        self.putInBackpack('AddressLine3', addressLine1)
        self.putInBackpack('City', city)
        self.putInBackpack(Anything.COUNTRYCOD_KEY, countryCode)
        self.putInBackpack(Anything.LABELS_KEY, label)
        self.putInBackpack('PlaceId', placeId)
        self.putInBackpack('Settings', settings)
        self.putInBackpack('State', state)
        self.putInBackpack('stationName', stationName)
        self.putInBackpack('Street', street)
        self.putInBackpack('Zipcode', zipcode)

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getIP(self):
        """
        This method gets the IP if exists in this structure
        :return: IP if exists
        """
        ip = self.getBackpack(Address.IP)
        if bool(ip):
            return ip[0]
        else:
            return []

    def getTimezone(self):
        """
        This method gets the timezone if exists in this structure
        :return: timezone value if exists
        """
        timezone =  self.getBackpack(Anything.TIMEZONE_KEY)
        if bool(timezone):
            return timezone[0]
        else:
            return []

    def getZipCode(self):
        """
        This method gets the postal code if exists in this structure
        :return: postal code value if exists
        """
        zipcode =  self.getBackpack(Anything.PCODE_KEY)
        if bool(zipcode):
            return zipcode[0]
        else:
            return []

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def setIP(self, ip):
        """
        This method adds a IP address to the object
        :return: True if the IP was added, false in other case
        """
        return self.putInBackpack(ip,Address.IP)


    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_address(dct):

        if dct is None:
            return dct

        a = dct
        listkeys = ['addressId', 'asn'] #ignored keys

        if 'addressId' in dct:
            a = Address(dct.get('addressId'))
            # The addressId is expected in base64

        elif 'postalCode' in dct:
            # for example, in devicePreferencess
            a = Address("temporary_id_by_postalCode:%s" % dct.get('postalCode'))

        elif 'asn' in dct:
            # This is for a JSON with info about an IP
            a = Address("temporary_id_by_ip:%s" % dct.get('ip'))

        if isinstance(a, Address):
            for k in dct:
                if k not in listkeys: a.putInBackpack(k, dct.get(k))

        return a

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------

    def __str__(self):
        return "------------\nAddress:\n------------\n%s" % super().__str__()

    def isRelatedWith(self, object):
        """
        This method is redefined to add special conditions for objects of type Route
        :param object: object to be checked
        :return: True if the object is related to this object, False in other case
        """
        res =  super().isRelatedWith(object)

        if isinstance(object, Route):
            destId = object.getDestinationId()
            origId = object.getOriginId()

            res = res or (destId is not None and destId == self.getId()) or (origId is not None and origId == self.getId())

        return res

    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------
    def eatAddress(self, object):
        "Eat object of this class"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Address)>> object type Address is expected")
            return False
        else: return self.eatSame(object)

    def eatRoute(self, object):
        "Only reads from Route in case it has any object idem to this"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(Address)>> object type Route is expected")
            return False

        # only eats information about the route if the id is contained in the destination or origin of the route
        if self.isRelatedWith(object):
            # add if not is included:
            self.putInBackpack(Anything.SUP_ROUTE_KEY, object.getId())

    def eatService(self, object):
        "Address does not read from Service"
        if not isinstance(object, Service):
            warnings.warn("eatService(Address)>> object type Service is expected")
        return False

    def eatUser(self, object):
        "Address does not read from User"
        if not isinstance(object, User):
            warnings.warn("eatUser(Address)>> object type User is expected")
        return False

    def eatDevice(self, object):
        "Address does not read from Device"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Address)>> object type Device is expected")
        return False

    def eatCard(self, object):
        "Address does not read from Card"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Address)>> object type Card is expected")
        return False

    def eatAction(self, object):
        "Address does nor read from Action"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Address)>> object type Action is expected")
        return False

    def eatActivity(self, object):
        "Address does not read from Activity"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Address)>> object type Activity is expected")
        return False


####################################
#           CLASS ROUTE
####################################
class Route(Anything):

    DESTINATION = 'Destination'
    ORIGIN = 'Origin'
    PREFERRED_TRANSPORT = 'PreferredTransportMode'
    TRANSPORT_NAMES = 'TransportNames'
    WAYPOINTS = 'Waypoints'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, destinationId, originId, preferredTransport=None, transportNames=None, waypoints=[]):
        self.id = "temporary id=source:%s,destination:%s" % (originId, destinationId)
        super().__init__(self.id, None)

        self.putInBackpack(self.ORIGIN, originId)
        self.putInBackpack(self.DESTINATION, destinationId)
        self.putInBackpack(self.PREFERRED_TRANSPORT, preferredTransport)
        self.putInBackpack(self.WAYPOINTS, waypoints)
        self.putInBackpack(self.TRANSPORT_NAMES, transportNames)


    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getDestinationId(self):
        return self.getBackpack(self.DESTINATION)

    def getOriginId(self):
        return self.getBackpack(self.ORIGIN)

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------

    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_route(dct):

        if 'destination' in dct:

            destination = dct.get('destination')
            dstId = None
            oriId = None
            if(destination!=None):
                destination = Address.as_address(destination)
                if destination is not None:
                    dstId = destination.getId()

            origin = dct.get('origin')
            if(origin!=None):
                origin = Address.as_address(origin)
                if origin is not None:
                    oriId = origin.getId()

            route = Route(dstId, oriId, dct.get(Route.PREFERRED_TRANSPORT),
                          dct.get(Route.TRANSPORT_NAMES), dct.get(Route.WAYPOINTS))

            if route is not None:
                if isinstance(destination, Address):
                    destination.addHistory("(as_route): this object belongs to route(id):%s" % route.getId())
                    route.addHistory("(as_route): detected address(id):%s" % destination.getId())
                    route.putInBackpack(Anything.OBJECTS_TO_PROCESS, destination)
                    destination.putInBackpack(Anything.SUP_ROUTE_KEY, route.getId())
                if isinstance(origin, Address):
                    origin.addHistory("(as_route): this object belongs to route(id):%s" % route.getId())
                    route.addHistory("(as_route): detected address(id):%s" % origin.getId())
                    route.putInBackpack(Anything.OBJECTS_TO_PROCESS, origin)
                    origin.putInBackpack(Anything.SUP_ROUTE_KEY, route.getId())

            return route

        return dct

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------

    def __str__(self):
        return "------------\nRoute:\n------------\n%s\n%s\n%s\n" % \
               (self.getDestinationId(), self.getOriginId(), super().__str__())

    def extractObjects(self):

        mlist = []
        d = self.getDestinationId()
        o = self.getOriginId()

        if d is not None: mlist.append(d)
        if o is not None: mlist.append(o)

        olist = super().extractObjects()

        for o in olist:
            mlist.append(o)

        return mlist

    def isRelatedWith(self, object):
        """
        This method is redefined to add special conditions for objects of type Address
        :param object: object to be checked
        :return: True if the object is related to this object, False in other case
        """
        res =  super().isRelatedWith(object)

        if isinstance(object, Address):
            res = res or (object.getId()==self.getDestinationId()) or (object.getId()==self.getOriginId())

        return res
    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------
    def eatAddress(self, object):
        "Route eat addresses if these are equal to origin or destination"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Route)>> object type Address is expected")
            return False

        #Add the address in case this is related with the address in the object
        if self.isRelatedWith(object):
            self.putInBackpack(Anything.SUP_ADDRESS_KEY, object.getId())
            # as is repeated info, do not list:
            self.addNotListable(Anything.SUP_ADDRESS_KEY)

    def eatRoute(self, object):
        "Route does not read from Route"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(Route)>> object type Route is expected")
            return False

        return self.eatSame(object)

    def eatService(self, object):
        "Route does not read from Service"
        if not isinstance(object, Service):
            warnings.warn("eatService(Route)>> object type Service is expected")

        return False

    def eatUser(self, object):
        "Route does not read from User"
        if not isinstance(object, User):
            warnings.warn("eatUser(Route)>> object type User is expected")

        return False

    def eatDevice(self, object):
        "Route does not read from Device"
        if not isinstance(object, Device):
            warnings.warn("eatUser(Device)>> object type Device is expected")

        return False

    def eatCard(self, object):
        "Route does not read from Card"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Route)>> object type Card is expected")

        return False

    def eatAction(self, object):
        "Route does nor read from Action"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Route)>> object type Action is expected")

        return False

    def eatActivity(self, object):
        "Address does not read from Activity"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Route)>> object type Activity is expected")

        return False

####################################
#           CLASS SERVICE
####################################
class Service(Anything):

    USER_NAME = 'username'
    ASSOCIATION_STATE = 'associationState'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, serviceName, associationState=None, userName=None):
        super().__init__(serviceName, None)

        self.putInBackpack('ServiceName', serviceName)
        self.putInBackpack(self.ASSOCIATION_STATE, associationState)
        self.putInBackpack(self.USER_NAME, userName)

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getServiceName(self):
        return self.getId()

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------

    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_service(dct):

        if 'services' in dct:

            states = dct.get('services')
            listofstates = []

            for s in states:
                s = Service(s.get('serviceName'), s.get('associationState'),  s.get('username'))
                listofstates.append(s)

            return listofstates

        return dct

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------

    def __str__(self):
        return "------------\nService:\n------------\n%s" % (super().__str__())


    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------

    def eatAddress(self, object):
        "Service does not read from Route"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Service)>> object type Address is expected")
        return False

    def eatRoute(self, object):
        "Service does not read from Route"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(Service)>> object type Route is expected")
        return False

    def eatService(self, object):
        "Service will read from Service only if is the same"
        return self.eatSame(object)

    def eatUser(self, object):
        "Service does not read from User"
        if not isinstance(object, User):
            warnings.warn("eatUser(Service)>> object type User is expected")
        return False

    def eatDevice(self, object):
        "Service does not read from Device"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Service)>> object type Device is expected")
        return False

    def eatCard(self, object):
        "Service does not read from Card"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Service)>> object type Card is expected")
        return False

    def eatAction(self, object):
        "Service does nor read from Action"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Service)>> object type Action is expected")
        return False

    def eatActivity(self, object):
        "Service does not read from Activity"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Service)>> object type Activity is expected")
        return False

####################################
#           CLASS ACTIVITY
####################################
class Activity(Anything):

    TYPE = 'itemType'
    UTTERANCEID = 'utteranceId'
    VERSION = 'version'
    TIMESTAMP = 'timestamp'
    MAIN_TEXT = 'mainText'
    VERSION = 'version'
    DATE_TIME = 'dateTime'
    TNIH = "TNIH"
    ENTRY_TIMESTAMP = 'timestamp(entry)'
    ENTRY_TIMESTAMP_RANGE = 'timestamp(range)'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, id, type=None, timestamp=None, utteranceId=None, version=1, maintext=None, deviceId=None,
                 datetime=None, userId=None, processId=True):

        super().__init__(id, None)  # this ID will change...

        # now, change id if needed:
        if processId: self.processId(id)

        self.putInBackpack(self.TYPE, type)
        self.putInBackpack(self.TIMESTAMP, timestamp)
        self.putInBackpack(self.MAIN_TEXT, maintext)
        self.putInBackpack(self.VERSION, version)
        self.putInBackpack(self.UTTERANCEID, utteranceId)
        self.putInBackpack(self.SUP_DEVICES_KEY, deviceId)
        self.putInBackpack(self.SUP_USERS_KEY, userId)

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------


    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getTimestamp(self):
        """
        Consult the timestamp linked to the activity
        :return: timestamp value
        """
        return self.getBackpack(self.TIMESTAMP)

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def processId(self, id):
        """
        Process the id to extract relevant info
        :param id:
        :return: this method modifies the structure of this object
        """
        # The ID is a string in base64 format. process:
        #try:
        id="%s==" % id
        print(id)
        dicto = json.loads(base64.b64decode(id))

        if isinstance(dicto, dict):
            # Get values:
            user = User(dicto.get('registeredUserId'))
            entryId = dicto.get('entryId')
            # Extract info from entryid:
            es = entryId.split('#')
            device = Device(es[2])
            device.setType(es[1])
            user.addDevice(device.getId())
            device.addUser(user.getId())

            self.putInBackpack(self.SUP_DEVICES_KEY, device.getId())
            self.putInBackpack(self.SUP_USERS_KEY, user.getId())
            self.putInBackpack(self.ENTRY_TIMESTAMP, es[0])
            self.putInBackpack(self.ENTRY_TIMESTAMP_RANGE, es[3])

            self.putInBackpack(Anything.OBJECTS_TO_PROCESS, device, eat=True)
            self.putInBackpack(Anything.OBJECTS_TO_PROCESS, user, eat=True)

            # change id:
            self.id = es[0]

        # Remember the original ID
        self.putInBackpack('originalId(base64)', id)


    def setUtteranceId(self, utteranceid):
        """
        This method analyses the structure setUtteranceId to extract the user and device (if any)
        :param utteranceid: value with an expected format
        :return: this method updates this object
        """
        if utteranceid is not None:
            self.putInBackpack(Activity.UTTERANCEID, utteranceid)

            # Update value for device:
            split = re.split(':|/|::', utteranceid)
            dev = Device(split[6],split[0])
            self.putInBackpack(Anything.SUP_DEVICES_KEY, dev.getId())
            self.putInBackpack(Anything.OBJECTS_TO_PROCESS, dev)

            # Update values for date and time
            try:
                dt = datetime.datetime(int(split[2]), int(split[3]), int(split[4]), int(split[8]), int(split[7]))
            except:
                self.putInBackpack('NotAllowedTime:', "%s:%s" % (split[8], split[7]))
                dt = datetime.datetime(int(split[2]), int(split[3]), int(split[4]))
                warnings.warn("setUtteranceId(Activity)>> Unexpected values in time")

            if len(split)==10:
                self.putInBackpack(Activity.TNIH, split[9])

            self.putInBackpack(Activity.DATE_TIME, dt)

    def getUser(self):
        """
        This method has been added to simplify the use of this object
        :return: the identificator of the user (if any)
        """
        return self.getBackpack(Anything.SUP_USERS_KEY)

    def getDevice(self):
        """
        This method has been added to simplify the use of this object
        :return: the identificator of the device (if any)
        """
        return self.getBackpack(Anything.SUP_DEVICES_KEY)

    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_activity(dct):

        if 'activityItemData' in dct:
            id = dct.get('id')

            if id is not None:
                a = Activity(id)
                passa = ['activityItemData', 'id', 'slots']
                aid = dct.get('activityItemData')

                if isinstance(aid, str): aid = json.loads(aid)

                slots = aid.get('slots')
                if slots is not None:
                    a.putInBackpack('Slots:', "%s" % slots)

                # First, check devices:
                devdescription = None
                dev = None
                if 'sourceDevice' in aid:
                    devdescription = aid.get('sourceDevice')

                elif 'sourceDeviceIds' in aid:
                    devdescription = aid.get('sourceDeviceIds')[0]

                if (devdescription != None):
                    dev = Device.as_device()

                # Check activity
                id = dct.get('id')

                if id is None:
                    # check if id present
                    if isinstance(dev, Device):
                        # is not an activity, but this works
                        return dev

                else:
                    # activity present
                    activity = Activity(id)

                    if (isinstance(dev, Device)):
                        usr = activity.getUser()
                        if len(usr) > 0:
                            usr = User(usr[0])
                            dev.addUser(usr.getId())
                            usr.addDevice(dev.getId())

                        # Add device to be processed:
                        dev.putInBackpack(Anything.SUP_ACTIVITY_KEY, activity.getId())
                        activity.putInBackpack(Anything.OBJECTS_TO_PROCESS, dev)
                        dev.addHistory("(as_activity): this object belongs to activity(id):%s" % activity.getId())
                        activity.addHistory("(as_activity): detected device(id):%s" % dev.getId())

                        # Add user to be processed:
                        usr.putInBackpack(Anything.SUP_ACTIVITY_KEY, activity.getId())
                        activity.putInBackpack(Anything.OBJECTS_TO_PROCESS, usr)
                        usr.addHistory("(as_activity): this object belongs to activity(id):%s" % activity.getId())
                        activity.addHistory("(as_activity): detected user(id):%s" % usr.getId())

                    # Rest of elements:
                    for item in aid:
                        if item not in passa:
                            activity.putInBackpack(item, aid.get(item))

            return a

        return dct


    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------

    def __str__(self):
        str = "\n------------\nActivity:\n------------\n%s\n" % super().__str__()

        return str

    def __cmp__(self, other):
        if isinstance(other, Activity):
            if (self.getTimestamp()>other.getTimestamp()):
                return 1
            elif (self.getTimestamp()<other.getTimestamp()):
                return -1
            else:
                return 0
        return None

    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------

    def eatAddress(self, object):
        "Address does not read from Route"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Activity)>> object type Address is expected")
        return False

    def eatRoute(self, object):
        "Activity does not read from Route"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(Activity)>> object type Route is expected")
        return False

    def eatService(self, object):
        "Activity does not read from Service"
        if not isinstance(object, Service):
            warnings.warn("eatService(Activity)>> object type Service is expected")
        return False

    def eatUser(self, object):
        "Activity does not read from User"
        if not isinstance(object, User):
            warnings.warn("eatUser(Activity)>> object type User is expected")
        return False

    def eatDevice(self, object):
        "Activity does not read from Device"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Activity)>> object type Device is expected")
        return False

    def eatCard(self, object):
        "Activity does not read from Card"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Activity)>> object type Card is expected")
        return False

    def eatAction(self, object):
        "Activity does nor read from Action"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Activity)>> object type Action is expected")
        return False

    def eatActivity(self, object):
        "Activity reads from Activity if are the same"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Activity)>> object type Activity is expected")
            return False
        return self.eatSame(object)


####################################
#           CLASS ACTION
####################################
class Action(Anything):

    DELETE_CARD_ACTION = 'DeleteCardAction'
    GIVE_FEEDBACK_ACTION = 'GiveFeedbackAction'
    THUMBS_UP_DOWN_ACTIVITY_ACTION = 'ThumbsUpDownActivityAction'
    PLAY_AUDIO_ACTION = 'PlayAudioAction'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, actionType, cardId=None):
        self.id = actionType # is an ID

        super().__init__(self.id, None)

        self.setCardId(cardId)

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    #def __del__(self):
    #    print("Action's object type(id):%s is died" % (self.getId()))

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getCardId(self):
        return self.getBackpack(Anything.SUP_CARDS_KEY)

    def getUser(self):
        return self.getBackpack(Card.REGISTERED_CUSTOMER_ID)

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def setCardId(self, cardId):
        if cardId is None:
            return None

        self.putInBackpack(Anything.SUP_CARDS_KEY, cardId)

        # get additional info from ID:
        userdev = cardId.split('#')
        if len(userdev) == 4:
            self.putInBackpack(Anything.SUP_USERS_KEY, userdev[0])
            # if(userdev[1]!=self.timestamp):
            #    print('Different Timestamps in Card. ID: %s, timestamp in JSON: %s' % (self.timestamp, userdev[1]))
            self.putInBackpack(Anything.TIMESTAMP_KEY, userdev[1])
            self.putInBackpack(Anything.SUP_DEVICES_KEY, userdev[3])

    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_action(dct):

        if((dct is None) or (len(dct)==0)):
            return dct

        if 'actionType' in dct:
            at = dct.get('actionType')

            a = Action(at)

            for i in dct:
                a.putInBackpack(i, dct.get(i))
                if(i == 'cardId'):
                    # Get additional values:
                    a.setCardId(dct.get(i))

            return a

        return dct

    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------

    def eatAddress(self, object):
        "Action does not read from Address"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Action)>> object type Address is expected")
        return False

    def eatRoute(self, object):
        "Action does not read from Route"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(Action)>> object type Route is expected")
        return False

    def eatService(self, object):
        "Service does not read from Address"
        if not isinstance(object, Service):
            warnings.warn("eatService(Action)>> object type Service is expected")
        return False

    def eatUser(self, object):
        "Action does not read from User"
        if not isinstance(object, User):
            warnings.warn("eatUser(Action)>> object type User is expected")
        return False

    def eatDevice(self, object):
        "Action does not read from Device"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Action)>> object type Device is expected")
        return False

    def eatCard(self, object):
        "Action does not read from Card"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Action)>> object type Card is expected")
        return False

    def eatAction(self, object):
        "Address will read from Action if is the same"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Action)>> object type Action is expected")
            return False
        return self.eatSame(object)

    def eatActivity(self, object):
        "Action does not read from Activity"
        if not isinstance(object, Activity):
            warnings.warn("eatAcrivity(Action)>> object type Activity is expected")
        return False


    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------

    def __str__(self):
        str = "\n------------\nAction:\n------------\n%s\n" % super().__str__()

        return str


####################################
#           CLASS CARD
####################################
class Card(Anything):

    TYPE = 'type'
    METRIC_ATTRIBUTES = 'metricAttributes'
    DELETE_CARD_ACTION = 'deleteCardAction'
    DESCRIPTIVE_TEXT = 'descriptiveText'
    GIVE_FEEDBACK_ACTION = 'giveFeedbackAction'
    HINT = 'hint'
    N_BEST_OPTIONS = 'nBestOptions'
    ORIGIN_INTENT_TYPE = 'originIntentType'
    PLAYBACK_AUDIO_ACTION = 'playbackAudioAction'
    PRIMARY_ACTIONS = 'primaryActions'
    PROMPT = 'PROMPT'
    REGISTERED_CUSTOMER_ID = 'User'
    SECONDARY_ACTIONS = 'secondaryActions'
    SUBTITLE = 'subtitle'
    CARD_TYPE = 'cardType'
    THUMBS_UP_DOWN_ACTIVITY_ACTION = 'thumbsUpDownActivityAction(Action id)'
    TITLE = 'title'
    TOKEN = 'token'
    WRAP_TITLE = 'wrapTitle'

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------
    def __init__(self, id, type=None, timestamp=None, metricAttributes=None, deleteCardAction=None,
                 descriptiveText='', giveFeedbackAction=None, hint=None, nBestOptions=None, originIntentType=None,
                 playbackAudioAction=None, primaryActions=None, prompt=None, registeredCustomerId=None,
                 secondaryActions=None, sourceDevice=None, subtitle=None, textCardType=None,
                 thumbsUpDownActivityAction=None, title=None, token=None, wrapTitle=None):

        super().__init__(id, None)

        self.setCardId(id)

        self.putInBackpack(Card.TYPE, type)
        self.putInBackpack(Anything.TIMESTAMP_KEY, timestamp)
        self.putInBackpack(Card.METRIC_ATTRIBUTES, metricAttributes)
        self.putInBackpack(Card.DELETE_CARD_ACTION, deleteCardAction)
        self.putInBackpack(Card.DESCRIPTIVE_TEXT, descriptiveText)
        self.putInBackpack(Card.GIVE_FEEDBACK_ACTION, giveFeedbackAction)
        self.putInBackpack(Card.HINT, hint)
        self.putInBackpack(Card.N_BEST_OPTIONS, nBestOptions)
        self.putInBackpack(Card.ORIGIN_INTENT_TYPE, originIntentType)
        self.putInBackpack(Card.PLAYBACK_AUDIO_ACTION, playbackAudioAction)
        self.putInBackpack(Card.PRIMARY_ACTIONS, primaryActions)
        self.putInBackpack(Card.PROMPT, prompt)
        self.putInBackpack(Card.REGISTERED_CUSTOMER_ID, registeredCustomerId)
        self.putInBackpack(Card.SECONDARY_ACTIONS, secondaryActions)
        self.putInBackpack(Anything.SUP_DEVICES_KEY, sourceDevice)
        self.putInBackpack(Card.SUBTITLE, subtitle)
        self.putInBackpack(Card.CARD_TYPE, textCardType)
        self.putInBackpack(Card.THUMBS_UP_DOWN_ACTIVITY_ACTION, thumbsUpDownActivityAction)
        self.putInBackpack(Card.TITLE, title)
        self.putInBackpack(Card.TOKEN, token)
        self.putInBackpack(Card.WRAP_TITLE, wrapTitle)

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    #def __del__(self):
    #    print("Card's object %s died" % (self.id))

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getTimestamp(self):
        return self.putInBackpack(Anything.TIMESTAMP_KEY)

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------

    def setCardId(self, id):
        self.cardId = id
        # get additional info from ID:
        #print(id)
        userdev = id.split('#')
        if (len(userdev) == 4):
            self.putInBackpack(Anything.SUP_USERS_KEY, userdev[0])
            self.putInBackpack(Anything.TIMESTAMP_KEY, userdev[1])
            self.putInBackpack(Anything.SUP_DEVICES_KEY, userdev[3])


    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_card(c):
        #rx = re.compile('|'.join(['activityItemData']))

        if 'cardMetricAttributes' in c:
            # Get actions:
            thumbsUpDownActivityAction = Action.as_action(c.get('thumbsUpDownActivityAction'))
            deleteCardAction = Action.as_action(c.get('deleteCardAction'))
            playbackAudioAction = Action.as_action(c.get('playbackAudioAction'))
            giveFeedbackAction = Action.as_action(c.get('giveFeedbackAction'))

            # Get devices:
            device = Device.as_device(c.get('sourceDevice'))

            # Rest of values:
            newC = Card(c.get('id'), c.get('cardType'), c.get('creationTimestamp'), c.get('cardMetricAttributes'),
                        None, c.get('descriptiveText'), None, c.get('hint'),
                        c.get('nBestOptions'), c.get('originIntentType'), None,
                        c.get('primaryActions'), c.get('prompt'), c.get('registeredCustomerId'),
                        c.get('secondaryActions'), None, c.get('subtitle'), c.get('textCardType'),
                        None, c.get('title'), c.get('token'), c.get('wrapTitle'))

            # Add objects:
            if thumbsUpDownActivityAction is not None:
                newC.putInBackpack(Card.THUMBS_UP_DOWN_ACTIVITY_ACTION, thumbsUpDownActivityAction.getId())
                newC.putInBackpack(Anything.OBJECTS_TO_PROCESS, thumbsUpDownActivityAction)
                thumbsUpDownActivityAction.addHistory("(as_card): this object belongs to card(id):%s" % newC.getId())
                newC.addHistory("(as_card): detected action(id):%s" % thumbsUpDownActivityAction.getId())
                thumbsUpDownActivityAction.putInBackpack(Anything.SUP_CARDS_KEY, thumbsUpDownActivityAction.getId())
            if deleteCardAction is not None:
                newC.putInBackpack(Card.DELETE_CARD_ACTION, deleteCardAction.getId())
                newC.putInBackpack(Anything.OBJECTS_TO_PROCESS, deleteCardAction)
                deleteCardAction.addHistory("(as_card): this object belongs to card(id):%s" % newC.getId())
                newC.addHistory("(as_card): detected action(id):%s" % deleteCardAction.getId())
                deleteCardAction.putInBackpack(Anything.SUP_CARDS_KEY, deleteCardAction.getId())
            if playbackAudioAction is not None:
                newC.putInBackpack(Card.PLAYBACK_AUDIO_ACTION, playbackAudioAction.getId())
                newC.putInBackpack(Anything.OBJECTS_TO_PROCESS, playbackAudioAction)
                playbackAudioAction.addHistory("(as_card): this object belongs to card(id):%s" % newC.getId())
                newC.addHistory("(as_card): detected action(id):%s" % playbackAudioAction.getId())
                playbackAudioAction.putInBackpack(Anything.SUP_CARDS_KEY, playbackAudioAction.getId())
            if giveFeedbackAction is not None:
                newC.putInBackpack(Card.GIVE_FEEDBACK_ACTION, giveFeedbackAction.getId())
                newC.putInBackpack(Anything.OBJECTS_TO_PROCESS, giveFeedbackAction)
                giveFeedbackAction.addHistory("(as_card): this object belongs to card(id):%s" % newC.getId())
                newC.addHistory("(as_card): detected action(id):%s" % giveFeedbackAction.getId())
                giveFeedbackAction.putInBackpack(Anything.SUP_CARDS_KEY, giveFeedbackAction.getId())
            if device is not None:
                newC.putInBackpack(Anything.SUP_DEVICES_KEY, device.getId())
                newC.putInBackpack(Anything.OBJECTS_TO_PROCESS, device)
                device.addHistory("(as_card): this object belongs to card(id):%s" % newC.getId())
                newC.addHistory("(as_card): detected device(id):%s" % device.getId())
                device.putInBackpack(Anything.SUP_CARDS_KEY, newC.getId())


            return newC

        return c

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        str = "\n------------\nCard:\n------------\n%s\n" % super().__str__()

        return str


    def __cmp__(self, other):
        if isinstance(other, Card):
            if (self.getTimestamp()>other.getTimestamp()):
                return 1
            elif (self.getTimestamp()<other.getTimestamp()):
                return -1
            else:
                return 0
        return None

    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------


    def eatAddress(self, object):
        "Card will read from Address only if is has relevant information about its own address"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Card)>> object type Address is expected")
        return False

    def eatRoute(self, object):
        "Card will read from Route only if it has relevant information about its own address"
        if not isinstance(object, Route):
            warnings.warn("eatAddress(Card)>> object type Address is expected")
        return False

    def eatService(self, object):
        "Card will read from Service only if it has relevant information about its own address"
        if not isinstance(object, Service):
            warnings.warn("eatService(Card)>> object type Service is expected")
        return False

    def eatUser(self, object):
        "Card will read from User only if it has relevant information about its own address"
        if not isinstance(object, User):
            warnings.warn("eatUser(Card)>> object type User is expected")
        return False

    def eatDevice(self, object):
        "Card will read from Device only if it has relevant information about its own address"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Card)>> object type Device is expected")
        return False

    def eatCard(self, object):
        "Card will read from Card only if it is the same object"
        if not isinstance(object, Card):
            warnings.warn("eatCard(Card)>> object type Card is expected")
            return False
        return self.eatSame(object)

    def eatAction(self, object):
        "Card will read from Action only if it has relevant information about its own address"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Card)>> object type Action is expected")
        return False

    def eatActivity(self, object):
        "Card will read from Activity only if it has relevant information about its own address"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Card)>> object type Activity is expected")
        return False

####################################
#           CLASS DEVICE
####################################
class Device (Anything):

    TYPE = 'Type'
    IDDEVICE = re.compile('|'.join(['deviceSerialNumber', 'deviceId', 'serialNumber']))

    #knwon IDs for type of device:
    TYPES = {"A3F1S88NTZZXS9":['Rio'],
             "A1DL2DVDQVK3Q":['Amazon music Android'],
             "A2825NDLA7WDZV":['Amazon music iOs'],
             "ATH4K2BAIXVHQ":['Amazon music Grover'],
             "A31ANRUHT2I2JF":['Amazon music Canary'],
             "A2IVLV5VM2W81":['Alexa Mobile Voice iOs'],
             "A2TF17PFR55MTB":['Alexa Mobile Voice Android'],
             "AB72C64C86AW2":['Amazon Echo API'],
             "A1MPSLFC7L5AFK":['Android Mobile']}


    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------

    def __init__(self, serialNumber, userID=None, type=None):

        super().__init__(serialNumber)
        #set color:
        #self.getContainer().setColor('red')
        if userID is not None: self.addUser(userID)


    # ---------------------------------
    #       GET METHODS
    # ---------------------------------

    def getType(self):
        return self.getBackpack(Device.TYPE)

    def getTypeDescription(self):
        type = self.getType()
        if type is not None and len(type)>0:
            description = self.TYPES.get(type[0])
            if description is not None and isinstance(description, list):
                return description[0]
        return None

    def getUser(self):
        """
        This method is included to simplify the use of this object
        :return: list of IDs from users related to this device (if any)
        """
        return self.getBackpack(Anything.SUP_USERS_KEY)

    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def addUser(self, userID):
        """
        This method is included to simplify the use of this object
        :param userID: identificator of the user of the device
        :return: True if the identificator for the user was added to this object, False in other case
        """
        if not isinstance(userID, str):
            warnings.warn("addUser(Device %s)>> Unexpected parameter %s, string is requested as ID" % (self.getId(),type(userID)))
            return False
        return self.putInBackpack(Anything.SUP_USERS_KEY, userID)

    def addAddress(self, addressID):
        """
        This method is included to simplify the use of this object
        :param addressID: identificator of the address of the device
        :return: True if the identificator for the address was added to this object, False in other case
        """
        if not isinstance(addressID, str):
            warnings.warn("addAddress(Device)>> Unexpected parameter, string is requested as ID")
            return False
        return self.putInBackpack(Anything.SUP_ADDRESS_KEY, addressID)

    def setType(self, type):
        if not isinstance(type, str):
            warnings.warn("setType(Device)>> Unexpected parameter, string is requested as type")
            return False
        self.putInBackpack(Device.TYPE, type)

    # ---------------------------------
    #       CHECKING METHODS
    # ---------------------------------
    def isIDKey(self, id1):
        """
        This method allows to check if a string can be used as keyword identifier for a device
        :param id1: string to be checked
        :return: True if the string 'id' is an identificator for Device. False in other case
        """
        if not isinstance(id1, str):
            warnings.warn("isIDKey(Device)>> Unexpected parameter, string is requested")
            return False
        return self.IDDEVICE.match(id1) # Also: Anything.SUP_DEVICES_KEY == Anything.getEquivalence(id1)


    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_device(dct):
        print(dct)

        if 'accountName' in dct:
            accname = dct.get('accountName')
            appdevl = dct.get('appDeviceList')
            ldev = []
            for d in appdevl:
                sn = d.get('serialNumber')
                if sn is not None:
                    nd = Device(sn)
                    nd.putInBackpack('AccountName', accname)
                    for k in d:
                        if k not in ['serialNumber']:
                            val = d.get(k)
                            print('key for device:%s, value:%s' % (k, val))
                            nd.putInBackpack(k, val)
                    ldev.append(nd)

            for c in dct:
                if c not in ['accountName', 'appDeviceList']:
                    val = dct.get(c)
                    for dev in ldev:
                        if val is not None: dev.putInBackpack(c, val)
            return ldev

        elif 'sourceDevice' in dct:
            return Device.as_device(dct.get('sourceDevice'))#dct.get('sourceDevice')

        elif 'appDeviceList' in dct:
            #process list
            adl = dct.get('appDeviceList')
            ld = []
            for da in adl:
                #device account:
                d = Device.as_device(da)
                print('appDeviceList!!!!>>> device: %s' % d)
                if isinstance(d, Device):

                    # get info about address:
                    da = Address.as_address(dct.get('deviceAddressModel'))
                    print('appDeviceList!!!!>>> address: %s' % da)

                    if isinstance(da, Address):
                        # complete info about address:
                        da.addHistory('This address was discovered in appDeviceList for device id=%s' % d.getId())
                        da.putInBackpack('temperatureScale', dct.get('temperatureScale'))
                        da.putInBackpack('locale', dct.get('locale'))
                        da.putInBackpack('timeZoneRegion', dct.get('timeZoneRegion'))
                        da.putInBackpack('temperatureScale', dct.get('temperatureScale'))
                        da.putInBackpack('timeZoneId', dct.get('timeZoneId'))
                        da.putInBackpack(Anything.SUP_DEVICES_KEY, d.getId())
                        d.putInBackpack(Anything.SUP_ADDRESS_KEY, da.getId())
                        d.putInBackpack(Anything.OBJECTS_TO_PROCESS, da)

                    # get additional info:
                    for v in dct:
                        if v not in ['appDeviceList', 'deviceAddressModel', 'deviceSerialNumber', 'deviceType',
                                     'temperatureScale', 'locale', 'timeZoneRegion', 'timeZoneId' ]:
                            d.putInBackpack(v, dct.get(v))


                    # append:
                    ld.append(d)

            return adl

        elif ('deviceSerialNumber' in dct) or ('serialNumber' in dct):
            id = dct.get('deviceSerialNumber')
            if id is None:
                id = dct.get('serialNumber')

            if id is None:
                #example: 211b100d593a50d4085a469a968a8d4e5a09b3fd.json, {'deviceSerialNumber': None, 'deviceType': None, 'preSharedKey': 'esc_iot_2018', 'securityMethod': 'WPA_PSK', 'ssid': 'ESC-IoT'}
                return dct

            d = Device(id)

            if ('deviceType' in dct) or ('type' in dct):
                t = dct.get('deviceType')
                if t is None:
                    t = dct.get('type')
                d.setType(t)

                desc = d.getTypeDescription()
                if desc is not None: d.putInBackpack('Type(description)', desc)

            for v in dct:
                if v not in ['deviceType', 'type', 'deviceSerialNumber', 'serialNumber']:
                    d.putInBackpack(v, dct.get(v))

            return d
        elif 'swVersion' in dct:
            print('sw version va a ser procesado!! que si que si ')
            # this happens, for example, in json of some devices (e.g. in Arlo)
            id = dct.get('id')
            if id is not None:
                d = Device(id)

                for v in dct:
                    if v not in ['id']:
                        d.putInBackpack(v, dct.get(v))
                print("objeto creado:%s" % d)
                return d
            print(id)

            return dct

        elif 'devicePreferences' in dct:
            listPref = dct.get('devicePreferences')
            devlist = []

            for pref in listPref:
                # preferences for a device
                applist = pref.get('appDeviceList')
                usr = pref.get('searchCustomerId')
                timezoneId = pref.get('timeZoneId')
                timezoneRegion = pref.get('timeZoneRegion')

                newa = Address.as_address(pref.get('deviceAddressModel'))
                if isinstance(newa, Address):
                    if timezoneId is not None: newa.putInBackpack('timeZoneId', timezoneId)
                    if timezoneRegion is not None: newa.putInBackpack('timeZoneRegion', timezoneId)

                for d in applist:
                    newd = Device.as_device(d)

                    for p in pref:
                        if p not in ['appDeviceList', 'searchCustomerId', 'timeZoneId', 'timeZoneRegion',
                                     'deviceAddressModel']:
                            newd.putInBackpack(p, pref.get('p'))

                    if isinstance(newd, Device):
                        if usr is not None:
                            newu = User(usr)
                            # add also ID for address:
                            if newa is not None: newu.putInBackpack(Anything.SUP_ADDRESS_KEY, newa.getId())
                            newd.addHistory('(as_device): User (id:%s) discovered in devicePreferences' % newu.getId())
                            newu.addHistory('(as_device): This user was discovered in devicePreferences for device id=%s' % newd.getId())
                            newu.putInBackpack(Anything.SUP_DEVICES_KEY, newd.getId())
                            newd.addUser(newu)
                            newd.putInBackpack(Anything.OBJECTS_TO_PROCESS, newu)

                        if newa is not None:
                            # add also ID for user:
                            if newu is not None: newa.putInBackpack(Anything.SUP_USERS_KEY, newu.getId())
                            newd.addHistory('(as_device): Address (id:%s) discovered in devicePreferences' % newa.getId())
                            newa.addHistory('(as_device): This address was discovered in devicePreferences for device id=%s' % newd.getId())
                            newd.addAddress(newa.getId())
                            newa.putInBackpack(Anything.SUP_DEVICES_KEY, newd.getId())
                            newd.putInBackpack(Anything.OBJECTS_TO_PROCESS, newa)

                        devlist.append(newd)

            return devlist
        return dct


    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        str = "\n------------\nDevice:\n------------\n%s" % super().__str__()

        return str

    def getIdGraph(self):
        type = self.getType()
        newname = super().getIdGraph()
        if type is not None:
            newname = ("%s\ntype:%s" % (newname, type))

            desc = self.getTypeDescription()
            if desc is not None:
                newname = "%s\ndesc:%s" % (newname, desc)

        return newname


    #def extractObjects(self):

    #    ul = self.getUsersID()

    #    mlist = [User(u).addDevice(self) for u in ul]
    #    olist = super().extractObjects()

    #    for o in olist:
    #        mlist.append(o)

    #    return mlist

    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------

    def eatAddress(self, object):
        "Device will read from Address only if it has relevant information about its own address"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Device)>> object type Address is expected")

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ADDRESS_KEY, object.getId())
            return True

        return False

    def eatRoute(self, object):
        "Device needs from route information about the addresses in case these are the same"

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ROUTE_KEY, object.getId())
            return True

        return False

    def eatService(self, object):
        "Device will read from Service only if it has relevant information about its own address"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(Device)>> object type Address is expected")

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_USERS_KEY, object.getId())
            return True

        return False

    def eatUser(self, object, destroyIfsame):
        "Device reads from the list of devices of the user to see if it is included"
        if not isinstance(object, User):
            warnings.warn("eatUser(Device)>> object type User is expected")
            return False

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_USERS_KEY, object.getId())
            return True

        return False

    def eatDevice(self, object):
        "Device eat from same type only if is the same"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(Device)>> object type Device is expected")
            return False

        mod = False
        if object.getId() == self.getId():
            if self.getType() is None:
                # try to assign
                self.setType(object.getType())
                mod = True
            elif object.getType() is not None and (len(object.getType()) > len(self.getType())):
                self.setType(object.getType())
                mod = True

        return mod or self.eatSame(object)

    def eatCard(self, object):
        """
        Device will read from card if, being related, the card has additional information that must be considered.
        For example, the card can have information about the user of the device
        """
        if not isinstance(object, Card):
            warnings.warn("eatCard(Device)>> object type Card is expected")

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the card if was not added:
            self.putInBackpack(Anything.SUP_CARDS_KEY, object.getId())
            # get information about potential users:
            users = object.getBackpack(Anything.SUP_USERS_KEY)
            for u in users:
                self.putInBackpack(Anything.SUP_USERS_KEY, u)
            return True

        return False

    def eatAction(self, object):
        "Device will read from Action only if it has relevant information about its own address"
        if not isinstance(object, Action):
            warnings.warn("eatAction(Device)>> object type Action is expected")

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ACTION_KEY, object.getId())
            return True

        return False

    def eatActivity(self, object):
        "Device read from activity in case it has a device"
        if not isinstance(object, Activity):
            warnings.warn("eatActivity(Device)>> object type Activity is expected")

        devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)

        if self.getId() in devlist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ACTIVITY_KEY, object.getId())
            return True

        return False

####################################
#           CLASS USER
####################################
class User (Anything):

    RELATIONSHIPSKEY = 'Relationships'
    IDUSER = re.compile('|'.join(['customerID', 'customerID', 'registeredUserID']))
    USER_EMAIL = 'email'
    USER_NAME = 'name'
    USER_FAMILY_NAME = 'familyName'
    NUM_USER_SYSTEM = 0

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------

    def __init__(self, userID, completeName=''):
        if userID is None:
            # this user need ahother ID:
            self.userId = User.NUM_USER_SYSTEM+1
            User.NUM_USER_SYSTEM += 1
            self.changeMyId = True
        else:
            self.userId = userID
            self.changeMyId = False

        others = {User.USER_NAME:[], User.USER_FAMILY_NAME:[], User.USER_EMAIL:[], User.RELATIONSHIPSKEY:[]}
        super().__init__(self.userId, others)

        #self.name = ''
        #self.family_name = ''

        if len(completeName)>0: self.setCompleteName(completeName)

        # set color
        #self.getContainer().setColor('magenta')

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    #def __del__(self):
    #    print("User's object %s died" % (self.id))

    # ---------------------------------
    #       GET METHODS
    # ---------------------------------

    def getName(self):
        """
        :return: Name of this user
        """
        #return self.name
        name = self.getBackpack(User.USER_NAME)

        if len(name)>0:
            return name[0]
        else: return ''

    def getFamilyName(self):
        """
        :return: Family name for this user
        """
        #return self.family_name
        famName = self.getBackpack(User.USER_FAMILY_NAME)
        if len(famName)>0:
            return famName[0]
        else:
            return ''


    def getCompleteName(self):
        """
        :return: user name + family name
        """
        return (self.getName() + self.getFamilyName())

    def getEmail(self):
        """
        :return: returns the email
        """
        email = self.getBackpack(User.USER_EMAIL)
        if len(email)>0:
            return email[0]
        else:
            return ''

    def getUserSignature(self):
        """
        :return: signature for this user
        """
        strret =''
        uname = self.getName()
        ufame = self.getFamilyName()
        if uname is not None and (isinstance(uname, str) and len(uname)>0):
            strret += uname[0] + ". "
        if ufame is not None:
            strret += ufame

        return strret

    def getStringsForSearch(self):
        """
        :return: list of strings that can be used for search information about this user
        """
        return [self.userName, self.userFamilyName, self.getCompleteName(), self.getUserSignature(), self.getUserID()]

    def getRealtionships(self):
        return self.getBackpack(self.RELATIONSHIPSKEY)

    def getDevices(self):
        """
        This method is included to simplify the use of this object
        :return: the devices included in the object
        """
        return self.getBackpack(Anything.SUP_DEVICES_KEY)


    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def setCompleteName(self,completeName):
        """
        Replace the familiy name of the user
        :param completeName: new complete name (Name and Family Name) of the user
        :return: True if was updated, False in other case
        """
        if completeName is None:
            return False

        initpos = completeName.find(' ')

        if(initpos!=-1):
            # two words:
            self.setName(completeName[:initpos])
            self.setFamilyName(completeName[initpos:])
        else:
            self.setName(completeName)
            self.setFamilyName('')

        return True

    def setName(self, name):
        """
        Replace the name of the user
        :param name: new name of the user
        """
        # self.name = name
        if isinstance(name, str) and len(name) > 0:
            return self.putInBackpack(User.USER_NAME, name, replace=True)
        else: return False

    def setFamilyName(self, familyName):
        """
        Replace the familiy name for the user
        :param familyName: new family name
        """
        #self.family_name = familyName
        if isinstance(familyName, str) and len(familyName)>0:
            return self.putInBackpack(User.USER_FAMILY_NAME, familyName, replace=True)
        else: return False

    def setEmail(self, email):
        """
        Replace the email for the user
        :param email: new email
        :return: True if was updated, False in other case
        """
        return self.putInBackpack(User.USER_EMAIL, email, replace=True)

    def addRelatedUser(self, userID):
        "Add a new user for this device using the ID of the user"
        self.putInBackpack(self.RELATIONSHIPSKEY, userID)

    def addDevice(self, devID):
        """
        This method is included to simplify the use of this object
        :param devID
        :return: True if the identificator for the device was included in this object, False in other case
        """
        if not isinstance(devID, str):
            warnings.warn("setDevices(Device)>> The identificator of the device must be a string value")
            return False

        return self.putInBackpack(Anything.SUP_DEVICES_KEY, devID)

    # ---------------------------------
    #       CHECKING METHODS
    # ---------------------------------

    def isEquivalentToUserID(self, id1):
        "Returns True if the string 'id' is an identificator for User"
        return self.IDUSER.match(id1)


    def isInString(self,string):
        "Returns True if the user is represented in the string"
        rx = re.compile('|'.join(self.getStringsForSearch()))
        return rx.match(string)


    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_user(dct):

        if 'authentication' in dct:
            #return dct.get('authentication')

            data_user = dct.get('authentication')

            if data_user is not None:
                userId = data_user.get('customerId')

                if userId is not None:
                    u = User(userId)
                    u.setCompleteName(data_user.get('customerName'))
                    u.setEmail(data_user.get('customerEmail'))
                    return u

        elif 'accounts' in dct:
            acc = dct.get('accounts')
            usrs = []
            for a in acc:
                #print('Initialising User...')

                if 'id' in a:
                    u = User(a.get('id'))
                    u.setCompleteName(a.get('fullName'))
                    u.setEmail(a.get('email'))
                    u.putInBackpack('role', a.get('role'))

                    usrs.append(u)

            return usrs

        else:
            # try as_userSystem:
            # no authentication, no accounts, try email and name as full name
            us = User(None, dct.get('name'))
            if us is not None:
                #try also url:
                us.putInBackpack('email', dct.get('email'))
                us.putInBackpack('url', dct.get('url'))
                return us

        return dct

    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        self.addNotListable(User.USER_NAME)
        self.addNotListable(User.USER_FAMILY_NAME)
        self.addNotListable(User.USER_EMAIL)
        str = "\n------------\nUser:\n------------\n"
        str = "%sComplete Name: %s\nEmail:%s\n%s" % (str, self.getCompleteName(), self.getEmail(), super().__str__())
        return str

    def __cmp__(self, other):
        if isinstance(other, Anything):
            if self.getId()==other.getId() or \
                    isinstance(other, User) and self.getEmail() is not None and other.getEmail() is not None and \
                    self.getEmail() == other.getEmail():
                return 0
            elif (self.getId()<other.getId()):
                return -1
            else:
                return 1
        return None

    def __lt__(self, other):
        return self.__cmp__(other) < 0


    def __eq__(self, other):
        if isinstance(other, Anything):
            return self.getId()==other.getId() or \
                    isinstance(other, User) and self.getEmail() is not None and other.getEmail() is not None and \
                    self.getEmail() == other.getEmail()

        return False

    def __hash__(self):
        return self.getId().__hash__()



    #----------------------------------
    #       ABSTRACT METHODS IMPLEMENTED
    #----------------------------------

    def eatAddress(self, object):
        "Only read from Address if has some info relevant to this user"
        if not isinstance(object, Address):
            warnings.warn("eatAddress(User)>> object type Address is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ADDRESS_KEY, object.getId())
            return True

        return False

    def eatRoute(self, object):
        "Only read from Route if has some info relevant to this user"
        if not isinstance(object, Route):
            warnings.warn("eatRoute(User)>> object type Route is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ROUTE_KEY, object.getId())
            return True

        return False

    def eatService(self, object):
        "Only eats if the name of the user is the same in the service than in the object user"

        if not isinstance(object, Service):
            warnings.warn("eatService(User)>> object type Service is expected")
            return False
        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_SERVICE_KEY, object.getId())
            return True

        return False

    def eatUser(self, object):
        "Only eats if the object is the same user"
        if not isinstance(object, User):
            warnings.warn("eatUser(User)>> object type User is expected")
            return False

        if self.__eq__(object) and self.changeMyId:
            self.id = object.getId()
            self.changeMyId = object.changeMyId

        return self.eatSame(object)

    def eatDevice(self, object):
        "Only eat the Device if the User's ID is included in the Device"
        if not isinstance(object, Device):
            warnings.warn("eatDevice(User)>> object type Device is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_DEVICES_KEY, object.getId())
            return True

        return False


    def eatCard(self, object):
        "Only eat card if the User's ID is included in the Card"

        if not isinstance(object, Card):
            warnings.warn("eatCard(User)>> object type Card is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_CARDS_KEY, object.getId())
            return True

        return False


    def eatAction(self, object):
        "Only eat action if the User's ID is included in the Action"

        if not isinstance(object, Action):
            warnings.warn("eatAction(User)>> object type Action is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ACTION_KEY, object.getId())
            return True

        return False


    def eatActivity(self, object):
        "Only eat Activity if the User's ID is included in the Activity"

        if not isinstance(object, Activity):
            warnings.warn("eatActivityUser)>> object type Activity is expected")
            return False

        userslist = object.getBackpack(Anything.SUP_USERS_KEY)

        if self.getId() in userslist:
            # add the user if was not added:
            self.putInBackpack(Anything.SUP_ACTIVITY_KEY, object.getId())

            # add info about devices in the activity if available:
            devlist = object.getBackpack(Anything.SUP_DEVICES_KEY)
            for d in devlist:
                self.addDevice(d)

            return True

        return False


####################################
#           CLASS CONTAINER
####################################
# To be used in graphs
class Container:
    NAME = 'name'
    ID = 'id'
    LAST_ID = -1

    def __init__(self, name):
        self.id = Container.LAST_ID + 1
        Container.LAST_ID += 1
        self.name = name
        self.color = None
        self.group = 0
        self.object = object
        self.label = str(self.id)

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getLabel(self):
        return self.label

    @staticmethod
    def getLabel(object=None):
        if object is None:
            return

    @staticmethod
    def getColor(object=None):
        if isinstance(object, Device):
            return 'red'
        elif isinstance(object, User):
            return 'magenta'
        elif isinstance(object, Card):
            return 'gray'
        elif isinstance(object, Service):
            return 'green'
        elif isinstance(object, Activity):
            return 'yellow'
        elif isinstance(object, Action):
            return 'orange'
        elif isinstance(object, Route):
            return 'darkviolet'
        elif isinstance(object, Address):
            return 'deepskyblue'
        else:
            return 'blue'

    @staticmethod #a different way for 'color' --> to be used with differnt html formats
    def getScore(object=None): #.range(["green", "yellow", "red", "blue", "purple", "white"]);
        if isinstance(object, Device):
            return 0.5 # red
        elif isinstance(object, User):
            return 0.83 # purple
        elif isinstance(object, Card):
            return 0.95 #gray
        elif isinstance(object, Service):
            return 0 #green
        elif isinstance(object, Activity):
            return 0.33 #yellow
        elif isinstance(object, Action):
            return 0.4 #orange
        elif isinstance(object, Route):
            return 0.83 #purple
        elif isinstance(object, Address):
            return 0.6 # purple
        else:
            return 1 #'white'

    @staticmethod
    def getShape(object=None):
        if isinstance(object, Device): #circle
            return 'diamond' #'o'
        elif isinstance(object, User): #square
            return 'square' #''s'
        elif isinstance(object, Card):
            return 'circle' #'v'
        elif isinstance(object, Service):
            return 'circle' #'>'
        elif isinstance(object, Activity): #diamond
            return 'circle' #'d'
        elif isinstance(object, Action):
            return 'circle' #'<'
        elif isinstance(object, Route):
            return 'circle' #'p'
        elif isinstance(object, Address):
            return 'triangle-down' #'h'
        else:
            return 'circle' #'blue'


    @staticmethod
    def getSize(object=None):
        if isinstance(object, Device): #circle
            return 40 #'o'
        elif isinstance(object, User): #square
            return 40 #''s'
        elif isinstance(object, Card):
            return 20 #'v'
        elif isinstance(object, Service):
            return 20 #'>'
        elif isinstance(object, Activity): #diamond
            return 20 #'d'
        elif isinstance(object, Action):
            return 20 #'<'
        elif isinstance(object, Route):
            return 20 #'p'
        elif isinstance(object, Address):
            return 20 #'h'
        else:
            return 10 #'blue'

    @staticmethod
    def getGroup(object=None):
        if isinstance(object, Device):
            return 0
        elif isinstance(object, User):
            return 0
        elif isinstance(object, Card):
            return 1
        elif isinstance(object, Service):
            return 1
        elif isinstance(object, Activity):
            return 2
        elif isinstance(object, Action):
            return 1
        else:
            return 3

    def setName(self, name):
        self.name = name

    def setColor(self, color):
        self.color = color

    def setLabel(self, label):
        self.label = label


####################################
#           CLASS CONTEXT
####################################
class Context:

    USER = User.__name__
    DEVICE = Device.__name__
    ACTIVITY = Activity.__name__
    SERVICE = Service.__name__
    ACTION = Action.__name__
    CARD = Card.__name__
    ADDRESS = Address.__name__
    ROUTE = Route.__name__
    SAVE_CONTEXT = 'results/context.txt' # Default file to print the context

    TYPES = [USER, DEVICE, ACTIVITY, SERVICE, ACTION, CARD, ADDRESS, ROUTE]

    # ---------------------------------
    #       CONSTRUCTOR
    # ---------------------------------

    def __init__(self):
        self.initmeplease()


    def initmeplease(self):
        """
        Initialises the context
        :return: True if the context was initialised, False in other case
        """
        # dict.fromkeys(Context.TYPES, []) # Generate dictionary, default values [] --- NO!!
        self.context = {Context.USER:[], Context.DEVICE:[], Context.ACTIVITY:[], Context.SERVICE:[], Context.ACTION:[],
                        Context.CARD:[], Context.ADDRESS:[], Context.ROUTE:[]}
        self.correlated=False

        return True

    # ---------------------------------
    #       DESTRUCTOR
    # ---------------------------------

    def __del__(self):
        print("Context is dead... :_(")

    # ---------------------------------
    #       STATIC METHODS
    # ---------------------------------
    @staticmethod
    def getTypes():
        "Returns the list of types (e.g. User, Device) considered in the context"
        return Context.TYPES

    @staticmethod
    def isType(typeitem):
        "Returns true if 'typeitem' is one of the types handled by the context (e.g. User)"
        if not isinstance(typeitem, str): return False
        return typeitem in Context.getTypes()
    # ---------------------------------
    #       GET METHODS
    # ---------------------------------
    def getSummary(self):
        """
        Allows to know a summary of the number of values in the context
        :return: dictionary with values for each class in the context and a string with the summary of results
        (usen the key 'summary')
        """
        keys = Context.getTypes()
        #summary = ["Type:%s, Number of elements:%s\n" % (k, len(self.getall(k))) for k in keys]
        summary = ''
        dicto = {}
        for k in keys:
            objects = self.getall(k)
            ne = "Type:%s, Number of elements:%s, " % (k, len(objects))
            dictoelement = {'number':len(objects)}
            # Percentage of relationships by type:
            types = Context.getTypes()

            # Statistics:
            #statistics = [0]*len(types)
            relti = ''
            tot = 0
            files = []
            for t in types:
                sum = 0
                for o in objects:
                    sum = sum + len(o.getBackpack(t))
                    files = list(set(files + o.getBackpack(Anything.FILES_KEY)))
                tot = tot + sum
                relti = "%s%s=%d  " % (relti, t, sum)
            cab = " Number of relationships:%d" % tot
            dictoelement.update({'relationships':tot})
            dictoelement.update({'files':len(files)})
            if tot>0:
                summary = "%s%s%s\n      %s\n" % (summary, ne, cab, relti)
            else:
                summary = "%s%s%s\n" % (summary, ne, cab)
            dicto.update({k:dictoelement})

        dicto.update({'summary':summary})

        return dicto #''.join(summary)

    def getKeys(self):
        """
        :return: list with the keys in the context
        """
        return self.context.keys()

    def isCorrelated(self):
        "Returns true if there are values in the context that must be updated/checked/correlated with the context"
        return self.correlated

    def setCorrelated(self, value):
        """If the input parameter is true, then this forces the system to correlate/update the objects. In other case,
           the correlation between the objects of the context is disabled"""
        if not isinstance(value, bool):
            warnings.warn('setCorrelated expects a ''bool'' value')
        self.correlated = value


    def getall(self, key=None):
        """
        :param: key: if None (by default) then no type is considered and the method returns all the objects in the
        context. If key is provided, then this is interpreted as a type of object, and only that type is provided.
        :return: all objects in the context in a single list
        """
        if key is None:
            return list(set([x for v in self.context.values() for x in v]))
        else:
            if not Context.isType(key):
                warnings.warn('getall>> key must be one of the following values:%s' % Context.getTypes())
            values = self.context.get(key)
            if values is None: values = []
            return values

    def getlistID(self, str=True):
        """ Returns the list of IDs in the context. By default this returns a list. This also returns a string if
            the parameter 'str' is set to True"""
        values = self.getall()
        listids = ["%s(id):%s\n" % (v.__class__.__name__, v.getId()) for v in values]
        if str: return ''.join(listids)
        else: return listids


    def getObjectWithId(self, objectId):
        """
        This method allows to recover an object from the structure based on its identificator (objectID)
        :param objectId: identificator of the object to be returned
        :return: object with the identificator equal to objectID
        """
        values = self.getall()
        objs_id = [v for v in values if v.getId()==objectId]
        if len(objs_id) > 1: warnings.warn('getObjectWithId>> unexpected!! more than one object with same ID')
        if len(objs_id) == 0:
            warnings.warn('getObjectWithId>> The object with ID %s does not exist' % objectId)
            return None
        return objs_id[0]

    def getObjects(self, objectsID, key=None):
        """
        This method allows to recover a list of objects from the structure based on its identificators
        :param objectsID: list of identificators (strings) of the objects.
        :param key: if None (by default) the list of objects is considered heterogeneous. This value when is not None
        is interpreted as a type of object to be accesed (e.g. User) simplifying the search.
        :return: a list of objects that matchs objectsID
        """
        if not isinstance(objectsID, list):
            warnings.warn('getObjects>> Unexpected parameter:%s, where a list of identificators for the objects must be provided' % objectsID)
            return []

        if Context.isType(key):
            # Get the objects using the key and select them based on objectsID:
            myobjs = self.getall(key)
        else:
            # Get the objects in the general list:
            myobjs = self.getall()

        if myobjs is None:
            return []


        objects = list(set([o for o in myobjs if o.getId() in objectsID ]))

        #for o in myobjs:
        #    print(objectsID)
        #    if o.getId() in objectsID:
        #        objects.append(o)

        return objects


    def isInContext(self, object):
        """
        Checks if the object is in this context
        :param object: object to be checked
        :return: True if the object is included in the context, False in other case
        """
        return isinstance(object, Anything) and object in self.getall()


    def searchKeywords(self, keywords, formatString=False):
        """
        :param keywords: a list of keywords
        :param formatString: False (default): returns a dictionary. True if a string with the type and ID of the
                             objects must be returned instead the dictionary.
        :return: by default returns a dictionary where each keyword is a key, and the values for each key are the
                objects in the context that contains the key.
         """
        if not isinstance(keywords, list):
            warnings.warn('searchKeywords>> Unexpected input parameter, a list of keywords is required')
            return None

        #Create a dictionary for the results:
        # dicto = dict.fromkeys(keywords, []) --> NOP!
        dicto = {}
        for k in keywords:
            dicto.update({k:[]})

        #values:
        values = self.getall()

        lftotal = []
        for k in keywords:
            lftotal = lftotal + ['------------ Keyword: %s -----------\n' % k]
            search_result = [o for o in values if o.__str__().find(k)>=0]
            dicto.update({k:search_result})

            #if formatstring:
            lf = ["%s(id):%s\n" % (o.__class__.__name__, o.getId()) for o in search_result]
            lftotal = lftotal + lf

        # All keywords:
        if len(dicto)>0:
            lftotal = lftotal + ['------------ Keywords: %s -----------\n' % keywords]
            intersection = dicto.get(keywords[0])
            rest_keys = keywords[1:len(keywords)]
            for k in rest_keys:
                values = dicto.get(k)
                intersection = list(set(intersection) & set(values))
            lf = ["%s(id):%s\n" % (o.__class__.__name__, o.getId()) for o in intersection]
            lftotal = lftotal + lf

        if formatString:
            lftotal = ''.join(lftotal)
            return lftotal
        else:
            return dicto

    def correlateNetworkAddresses(self, list_addresses, storehistory=False):
        """
        This method gets a list of Addresses with information about public IPs, and then correlates
        the info in the context for the devices. Then, this returns the matches found (if any)
        :param list_addresses: list of Addresses with information about IPs (in string format)
        :param storehistory: if True stores in the object device the history of the matches. This param is False by def.
        :return: a string with the matches found (if any)
        """
        "Correlate network addresses with devices and/or locations"

        if list_addresses is None:
            warnings.warn('correlateNetworkAddresses>> Unexpected input parameter, a list of IP addresses is required')
            return None

        # 1. Get devices
        mydevs = self.getall(Context.DEVICE)
        if len(mydevs) == 0: return None

        # 2. Retain only devices with addresses:
        mydevs = [d for d in mydevs if len(d.getBackpack(Anything.SUP_ADDRESS_KEY))>0]

        # 2. Recover addresses for the devices
        #addresses = list(set([d.getBackpack(Anything.SUP_ADDRESS_KEY) for d in mydevs]))
        #addresses = [a for alist in addresses for a in alist] # Unique list
        #addresses = self.getObjects(addresses, Context.ADDRESS)

        # 4. Check for matches and prepare string:
        if bool(mydevs):
            strretTot = 'Searching matches for:\n'
        else:
            strretTot = 'There are no devices with addresses for the comparison'

        for d in mydevs:
            strret = '-----------------------\nDevice(id=%s):\n-----------------------\n' % d.getId()
            # Check if the address for this device has matches:
            dev_add = d.getBackpack(Anything.SUP_ADDRESS_KEY)
            dev_add = self.getObjects(dev_add, Context.ADDRESS)

            matchesTimezone = [[apub, adev] for apub in list_addresses for adev in dev_add if
                               bool(apub.getTimezone()) and apub.getTimezone() == adev.getTimezone()]
            matchesZipcode = [[apub, adev] for apub in list_addresses for adev in dev_add if
                              bool(apub.getZipCode()) and apub.getZipCode() == adev.getZipCode()]

            if len(matchesTimezone)+len(matchesZipcode) > 0:
                #strret = 'Device(id=%s) with Address(id=%s, timezone=%s, postalcode=%s):\n' % \
                #         (d.getId(), dev_add.getId(), dev_add.getTimezone(), dev_add.getZipCode())

                for mt in matchesTimezone:
                    apub = mt[0]
                    adev = mt[1]
                    strret = "%s   -> Public IP %s with timezone %s and postal code %s, for address ID %s [MATCH Address %s]\n" % \
                             (strret, apub.getIP(), apub.getTimezone(), apub.getZipCode(), apub.getId(), adev.getId())

                for mt in matchesZipcode:
                    apub = mt[0]
                    adev = mt[1]
                    strret = "%s   -> Public IP %s with postal code %s, for address ID:%s\n [MATCH Address %s]" % \
                             (strret, apub.getIP(), apub.getZipCode(), apub.getId(), adev.getId())

                    # Add to the historic
                    d.addHistory(strret)
                strretTot = '%s%s' % (strretTot, strret)
            else:
                strretTot = '%s%s -- No matches found for timezone and zipcode\n' % (strretTot, strret)

        return strretTot


    # ---------------------------------
    #       MODIFICATION METHODS
    # ---------------------------------
    def setObjectsInContext(self, objects, key=None):
        """
        :param objects: list of objects to be replaced in the context.
        :param key: Type of the objects to be replaced. If this is not provided (by default None) then the method
                    considers that the objects are heterogeneous. If this is provided, the entire input for type key is
                    updated to the list of objects.
        :return: Empty list [] if all the objects were replaced, or a list with the objects that weren't replaced if any.
        """
        if objects is None or not isinstance(objects, list):
            warnings.warn('updateObjectsInContext>> Unexpected input parameters, objects must be a list of objects to be replaced')
            return objects

        if key is not None:
            self.context.update({key:objects})

        else:
            for o in objects:
                self.setObjectInContext(o)

        # The context must be updated
        print('Objects included in the context, please call to cannibalism!!')
        self.setCorrelated(False)


    def setObjectInContext(self, object, replace=True, eat=False):
        """
        :param object: object to be added, replaced or eaten. By default this method replaces an object in the context.
        :param replace: if True (default) then the object is replaced to the new value if exists in the context. If
                        False then the object is not replaced if this exists in the context.
        :param eat: if True then the object is not replaced. Instead, the object in the context "eat" the new object
                    if this exist in the context. If this parameter is true, then 'replace' is set up to False.
        :return: this method modifies the object Context; the method returns 0 if no changes were made, 1 if the object
                 was added (new object), 2 if the object was eaten and 3 if the object was updated to the new one.
        """
        "Update a single object in the context. By default this replaces the object with the new value it exists."
        if not isinstance(object, Anything):
            return None
        k = object.__class__.__name__
        vals = self.getall(k)
        ret = 0

        if eat: replace = False

        if vals is None or len(vals)==0:
            self.context.update({k:[object]})
            ret = 1
        else:
            if object not in vals:
                vals.append(object)
                self.context.update({k:vals})
                ret = 1
            else:
                index = vals.index(object)
                if eat:
                    vals[index].eat(object)
                    ret = 2
                elif replace:
                    vals[index] = object
                    ret = 3
                self.context.update({k:vals})

        # The context must be updated
        print(Fore.YELLOW, end='')
        print('Object Type:%s id:%s included in the context, please call to cannibalism!!' %
              (object.__class__.__name__, object.getId()))
        print(Style.RESET_ALL, end='')
        self.setCorrelated(False)

        return ret

    def cannibalism(self):
        """
        This function updates the entire context: the elements eat each other
        :return: True if the context was updated. False in other case
        """
        if self.isCorrelated():
            print("'I'm not hungry to become a cannibal', says the context")
            return False
        else:
            print(Fore.BLUE)
            print("Running in cannibal mode... updating the context ")
            print(Style.RESET_ALL)

        keys = self.getKeys()
        aval = self.getall()

        print('Updating context... number of elements: %d ... please, wait ... ' %(len(aval)))
        mod = False
        for k in keys:
            values = self.getall(k)
            newval = []
            #1.- Set bidirectional relationships:
            for v in values:
                for o in aval:
                    mod = mod or v.eat(o)
                newval.append(v)
            self.setObjectsInContext(newval, k)
        print('done! ')
        self.setCorrelated(True)
        return mod


    def addItem(self, object):
        """
        :param object: object (instance of Anything) to be added to the context
        :return: True if the object was added to the context, False in other case
        """
        if not isinstance(object, Anything):
            warnings.warn('addItem>> Unexpected input parameters type %s value:%s, instance of Anything is required' % (type(object), object))
            return False
        # 1.- Check if there are objects to be processed in the object and add them to the context first:
        my_obj = object.getObjectsForProcessing()

        for o in my_obj:
            self.addItem(o)

        # 2.- Set up the object in the context:
        return self.setObjectInContext(object, eat=True) > 0

        # 3.- Update the entire context for the element:
        self.cannibalism()


    # ---------------------------------
    #       JSON OBJECT DECODING METHODS
    # ---------------------------------
    @staticmethod
    def as_context(dct):
        if 'destination' in dct:
            r = Route.as_route(dct)
            #print('Calling as_route:%s, returned:%s' % (dct,r))
            return r

        elif 'activityDialogItems' in dct:
            vals = dct.get('activityDialogItems')
            if len(vals)>0 and isinstance(vals[0], Anything):
                return vals

            lactivities = []
            for a in vals:
                #print('Calling as_activity - activityDialogItems found:%s' % a, end='')
                na = Activity.as_activity(a)
                #print(', returned:%s' % na)
                if isinstance(na, Anything):# can be a device
                    lactivities.append(na)
            return lactivities

        elif 'activityItemData' in dct:
            #print('Calling as_activity - activityItemData found:%s' % dct)
            a = Activity.as_activity(dct)
            #print(', returned:%s' %  a)
            return a


        elif 'authentication' in dct or 'accounts' in dct:# or ('name' in dct and 'email' in dct):
            u = User.as_user(dct)
            #print('Calling as_user:%s, returned:%s' % (dct, u))
            return u

        elif 'services' in dct:
            s = Service.as_service(dct)
            #print('Calling as_service:%s, returned:%s' % (dct, s))
            return s

        elif 'devices' in dct:
            # list of devices:
            vals = dct.get('devices')
            ldevs = []
            for d in vals:
                nd = Device.as_device(d)
                #print('Calling as_device:%s, returned:%s' % (d, nd))
                if isinstance(nd, Device):
                    ldevs.append(nd)
                elif isinstance(nd, list):
                    ldevs += nd

            return ldevs

        elif 'cards' in dct:
            # List of cards:
            vals = dct.get('cards')
            lcards = []
            for c in vals:
                nc = Card.as_card(c)
                #print('Calling as_card:%s, returned:%s' % (c, nc))
                if isinstance(nc, Card):
                    lcards.append(nc)
            return lcards

        # elif 'values' in dct:

        elif 'devicePreferences' in dct:

            return Device.as_device(dct)

            """
            ldevs = []
            values = dct.get('devicePreferences')

            for adl in values:
                #Get account details:
                devacc_list = adl.get("appDeviceList")
                for d in devacc_list:
                    nv =  Device.as_device(d)
                    #print('Calling as_device:%s, returned:%s' % (adl, nv))
                    if isinstance(nv, list) and len(nv)>0 and isinstance(nv[0], Anything):
                        ldevs = ldevs + nv

            return ldevs
            """

        elif 'deviceSerialNumber' in dct or 'serialNumber' in dct \
                or 'sourceDevice' in dct or 'swVersion' in dct:
            d = Device.as_device(dct)
            #print('Calling as_device:%s, returned:%s' % (dct,d))


        elif 'bluetoothStates' in dct:

            listDev = dct.get('bluetoothStates')
            Bdevices = []

            for d in listDev:
                bd = Device.as_device(d)
                #print('Calling as_device:%s, returned:%s' % (dct, bd))
                if (isinstance(bd, Device)):
                    Bdevices.append(bd)

            return Bdevices


        # elif 'customerWriteToCalendarMap' in dct:

        # elif 'lists' in dct:

        elif 'activities' in dct:
            listAct = dct.get('activities')
            activities = []

            for a in listAct:
                ac = Activity.as_activity(a)
                #print('Calling as_activity:%s, returned:%s' % (dct, ac))
                if (isinstance(ac, Activity)):
                    activities.append(ac)

            return activities

        # elif 'notifications' in dct:

        elif 'ationType' in dct:
            a = Action.as_action(dct)
            #print('Calling as_action:%s, returned:%s' % (dct, a))
            return a

        #else:
            # do nothing
            #print('Nothing to do with this input: %s'%dct)

        return dct

    # ---------------------------------
    #       USE THIS OBJECT
    # ---------------------------------
    def showContext(self, output='context', objectsofinterest=[User.__name__, Device.__name__], mode=0):
        """
        Shows graphically the relationships between users and devices in the context
        :param output: name of the file for the output, 'context' by default
        :param objectsofinterest: list of types to select the objects of interest. If [] then all the objects are shown.
        by default the objects of interest are Users and Devices ['User', 'Device']
        :param mode: if 0 (by default) prints only the graphviz graph. if 1 prints the graph in a web browser. if 2
        then both options are enabled
        :return: If mode>0 then the handler of the http connection. In other case, returns the name of the file used
        """
        res = False
        if objectsofinterest is None or len(objectsofinterest)==0:
            objectsofinterest = Context.getTypes()

        rx = re.compile('|'.join(objectsofinterest))

        G1 = pgv.AGraph(directed=True)  # MACs
        G2 = nx.DiGraph()
        #print('objects of interest:%s' % objectsofinterest)
        for t in self.context:
            # This is the key:
            if rx.match(t):
                objects = self.context.get(t)

                for o in objects:
                    # Add a node for the object:
                    ocontainer = o.getContainer()
                    G1.add_node(ocontainer.getName())
                    G2.add_node(ocontainer.getID(), name=ocontainer.getName(), label=ocontainer.getID(),
                                group=Container.getGroup(o), color=Container.getColor(o))

                    # Add relationships with other objects:
                    objlist = self.getObjects(o.getRelatedIDs()) # all objects
                    objlist = [ol for ol in objlist if ol.getId()!=o.getId() and ol.__class__.__name__ in objectsofinterest] #only objects of interest
                    #print('object:%s, container id:%s, objects of interest:%s' % (o.getId(), ocontainer.getID(), objlist))
                    for o2 in objlist:  # devlist:
                        # Get object:
                        o2container = o2.getContainer()
                        G1.add_node(o2container.getName())
                        G1.add_edge(ocontainer.getName(), o2container.getName())

                        G2.add_node(o2container.getID(), name=o2container.getName(), label=o2container.getID(),
                                    group=Container.getGroup(o2), color=Container.getColor(o2),
                                    type=Container.getShape(o2), size=Container.getSize(o2), score=Container.getScore(o2))
                        G2.add_edge(ocontainer.getID(), o2container.getID())

            else:
                print("%s not match with objects of interest" % t)

        if mode!=1:
            if output is None:
                output = 'context' #we need a file to write the output
            G1.write('results/' + output + '.dot')
            G1.layout()  # default to neato
            G1.layout(prog='dot')  # use dot
            G1.draw('results/' + output + '.gif')

            res = output + '.gif'

        #nx.draw(G2, with_labels=True)
        #plt.savefig(output+'.png')

        if mode>0:
            d = json_graph.node_link_data(G2)
            json.dump(d, open('force/force.json', 'w'))

            # Serve the file over http to allow for cross origin requests
            httpd = http_server.load_url('force/force2.html')

            return httpd

            """
            app = flask.Flask(__name__, static_folder="force")

            @app.route('/')
            def static_proxy():
                return app.send_static_file('force/force.html')

            print('\nGo to http://localhost:8000/force/force.html to see the example\n')
            app.run(port=8000)
            # the handler to stop the server httpd.stop()
            return app
            """


        return res


    def save_context(self, filename):
        try:
            orig_stdout = sys.stdout
            f = open(filename, 'w')
            sys.stdout = f

            print(self)

            sys.stdout = orig_stdout
            f.close()
            return True
        except:
            return False



    # ---------------------------------
    #       REDEFINED METHODS
    # ---------------------------------
    def __str__(self):
        str = 'Current CONTEXT:\n'
        keys = Context.getTypes()

        for k in keys:
            lo = self.getall(k)
            for o in lo:
                str = "%s%s" % (str,o.__str__())

        return str


    ####################################
    #       FEEDING THE CONTEXT
    ####################################
    @staticmethod
    def getFiles(directory, dicto={}, extensions=['.json'], recursive=True):
        """
        This method helps to get all files with extension in extension in a directory recursively
        :param directory: path to the first directory
        :param dicto: directory structure, empty by default
        :param extension: a list with the extension of files to be returned (.json by default)
        :param recursive: if True (by default) the method explores the directories inside the main directory
        :return: a dictionary were the keys are the extension of the
        """
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = "%s/%s" % (root, filename)
                extension = os.path.splitext(filepath)[1]
                if extension in extensions:
                    vals = dicto.get(extension)
                    if vals is None: vals = []
                    vals.append(filepath)
                    dicto.update({extension:vals})

            if recursive:
                for dictoSon in dirs:
                    dicto2 = Context.getFiles(dictoSon, dicto, extensions)
                    # combine directories:
                    for k in dicto2:
                        vals = dicto.get(k)
                        if vals is None: vals=[]
                        vals2 = dicto2.get(k)
                        if vals2 is None: vals2=[]
                        vals = vals + vals2
                        dicto.update({k:vals})
        return dicto

    def createContextFromJson(self, pathtoJsonFiles, showContext=False, printToFile=SAVE_CONTEXT):
        """
        This method initialises the context
        :param pathtoJsonFiles: path to the list of .json files, or, instead a list with the path of the files
        :param showContext: if False (default) shows the context once the method finalises
        :param printToFile: file to save the context
        :return: The list of files processed (if any)
        """
        if not (isinstance(pathtoJsonFiles, str) or isinstance(pathtoJsonFiles, list)):
            raise ValueError('createContextFromJson requires either a path for the folder of json files or a list '
                             'with the path of the files to be added')
            return []

        if not self.initmeplease():
            warnings.warn('createContextFromJson>> Object not initiated')
            return []

        files_processed = []
        if isinstance(pathtoJsonFiles, str):
            # Get all files related:
            filepaths = self.getFiles(pathtoJsonFiles, {}, ['.json'], False)
            if len(filepaths)>0: filepaths = filepaths.get('.json')
        else:# list of strings
            filepaths = pathtoJsonFiles

        if filepaths is not None and len(filepaths)>0:
            for filepath in filepaths:
                filename = ntpath.basename(filepath)
                print(filename)
                with open(filepath) as df:
                    data = json.load(df, object_hook=Context.as_context)
                    df.close()

                if isinstance(data, list):
                    for d in data:
                        if isinstance(d, Anything):
                            print(d)
                            d.addRelatedFiles(filename)
                            self.addItem(d)
                            files_processed.append(filepath)

                elif isinstance(data, Anything):
                    print(data)
                    data.addRelatedFiles(filename)
                    self.addItem(data)
                    files_processed.append(filepath)

                if data is None or ((isinstance(data, list) or isinstance(data, dict)) and len(data) == 0):
                    print("No Item info found in:", filepath)

            # Now, call to cannibalism to update the context
            self.cannibalism()

            # All the items for the context in context
            self.save_context(printToFile)

            if showContext:
                self.showContext()

            files_processed = list(set(files_processed))

            return files_processed

        else:
            warnings.warn('createContextFromJson>> Context not created, there are no files to be analysed')
            return []


####################################
#          TESTING METHODS
####################################
def checkContextGeneration():
    "Check if the context can be generated"

    # Two objects:
    user1 = User("123userID", "Ana Nieto")
    user2 = User("324userID")
    user2.setCompleteName('Carambola')
    user2.setEmail('email@email.com')

    # One device. The device knows that his user is user1 (id:123userID).
    device = Device("1436deviceID")
    device.addUser(user1.getId())
    device.addUser(user2.getId())

    user2.addDevice(device.getId()) # User2 will add this device, and adds to the device in his profile user2 as user.

    """
    print(device.getEquivalence('User'))
    print(device.getEquivalence('user'))
    print(device.getEquivalence('User(id)'))
    print(device.getEquivalence('Device'))
    """

    print(device)


    # Check equivalences:
    """
    for k in Anything.TYPES:
        print("equivalence for type:%s, equal to:%s" % (k, device.getEquivalence(k)))

    for k in Anything.TYPES:
        device.putInBackpack(k, 'updating type %s' % k)
        print(device)
    """
    # Create the context:
    context = Context()

    # Add info to context:
    context.addItem(user1)
    context.addItem(user2)
    context.addItem(device)

    context.cannibalism()

    # when the device is added this has to recognise the rest of information. The device in user2 is the same but
    # with more information, the device in user2 knows that user2 is also his user.

    print(context)
    context.showContext()

    return context


