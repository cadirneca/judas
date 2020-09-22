import os, sys
import logging
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = current_dir + '/..'
sys.path.insert(0, current_dir)
sys.path.insert(0,app_dir)

from os import listdir
from os.path import isfile, join
from auxiliar.external.thehive.TheHiveConnector import TheHiveConnector
from auxiliar.external.thehive.common import getConf

class JudasConnector:
    'JUDAS connector'

    #observables
    OB_AUTONOMOUS_SYSTEM = "autonomous_system"
    OB_DOMAIN = "domain"
    OB_FILE = "file"
    OB_FILENAME = "filename"
    OB_FQDN = "fqdn"
    OB_HASH = "hash"
    OB_IP = "ip"
    OB_MAIL = "mail"
    OB_MAIL_SUBJECT = "mail_subject"
    OB_OTHER = "other"
    OB_REGEXP = "regexp"
    OB_REGISTRY = "registry"
    OB_URI_PATH = "uri_path"
    OB_URL = "url"
    OB_USER_AGENT = "user-agent"

    #equivalences
    OB_EQUIVALENCE = {
        OB_AUTONOMOUS_SYSTEM:[],
        OB_DOMAIN:[],
        OB_FILE:[],
        OB_FILENAME:[],
        OB_FQDN:[],
        OB_HASH:[],
        OB_IP:[],
        OB_MAIL:[],
        OB_MAIL_SUBJECT:[],
        OB_OTHER:[],
        OB_REGEXP:[],
        OB_REGISTRY:[],
        OB_URI_PATH:[],
        OB_URL:[],
        OB_USER_AGENT:[]
    }

    def __init__(self, cfg):
        self.logger = logging.getLogger('workflows.' + __name__)
        self.cfg = cfg

    def scan(self, mypath):
        '''
        :param folder: folder with the contexts
        :return: list of files for contexts
        '''
        self.logger.info('%s.scan starts', __name__)
        return [f for f in listdir(mypath) if isfile(join(mypath, f))]

    @staticmethod
    def getObservableTypeEquivalence(name):
        """
        :param name: name to search the equivalent term to define the observable
        :return: official name for the observable in thehive
        """
        ob_names = JudasConnector.OB_EQUIVALENCE.keys()
        for n in ob_names:
            if n.upper() == name.upper(): return n
            values = JudasConnector.OB_EQUIVALENCE.get(n)
            for v in values:
                if v.upper() == name.upper(): return n
        return JudasConnector.OB_OTHER


def connectJudas(pathfile):
    logger = logging.getLogger(__name__)
    logger.info('%s.connectJudas starts', __name__)

    report = dict()
    report['success'] = bool()

    try:
        cfg = getConf()
        #judasConnector = JudasConnector(cfg)
        theHiveConnector = TheHiveConnector(cfg)

        #Get JSON from file:
        with open(pathfile) as f:
            context = json.load(f)

        # check if the case exists:
        #esCaseId = theHiveConnector.searchCaseByDescription(context.get('description')) # not working
        esCaseId = None

        if esCaseId is None:
            # get values for the new case
            caseTitle = context.get('title')
            caseDescription = context.get('description')
            caseTags = context.get('tags')

            # add new case
            case = theHiveConnector.craftCase(caseTitle, caseDescription, caseTags)
            createdCase = theHiveConnector.createCase(case)
            esCaseId = createdCase.id  # caseUpdated.id

            # create task
            #commTask = theHiveConnector.craftCommTask()
            #commTaskId = theHiveConnector.createTask(esCaseId, commTask)

            # observables
            observables = context.get('observables')
            for o in observables:
                try:
                    if o['dataType'] == JudasConnector.OB_FILE:
                        theHiveConnector.addFileObservable(esCaseId, o['data'], o['comment'])
                    else:
                        theHiveConnector.addObservable(esCaseId, o['data'], o['dataType'], o['comment'], o['tags'], o['tlp'])
                except Exception as e:
                    logger.error("Exception while adding observable: %s, %s" % (o, e))
            print("New case with ID: " + esCaseId)

        else:
            print("Found case with ID: " + esCaseId)

    except Exception as e:
        logger.error('Failed to get unload contexts', __name__, exc_info=True)
        report['success'] = False
        raise




