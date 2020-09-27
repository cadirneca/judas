#!/usr/bin/env python3
# encoding: utf-8

import os,sys

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = current_dir + '/..'
sys.path.insert(0, current_dir)
sys.path.insert(0,app_dir)

from cortexutils.analyzer import Analyzer

from auxiliar import auxiliar as aux
# configuration parameters are loaded using getConf
from auxiliar.external.thehive.common import getConf
from ju_eaters import eatingJson as eatj
import zipfile
from os.path import basename

class JudasAnalyzer(Analyzer):
    """This is the analyzer for JUDAS, please take into account that this only adds the feature for analysing JSON
       files"""

    def __init__(self):
        """Initialization of the class. Here normally all parameters are read using `self.get_param`
        (or `self.getParam`)"""
        Analyzer.__init__(self)

    def run(self):
        """This is called when running the class, as you can see at the __main__ part below. Remember to always report a
        python dictionary. """
        # get config
        self.cfg = getConf()

        #1.- get parameters
        filepath = self.get_param('file', None, 'File is missing')
        base = os.path.basename(filepath) # file with extension
        base = os.path.splitext(base)[0] # filename without extension

        path = os.path.dirname(os.path.abspath(filepath))
        aux.createFolder('sources', path)
        sources = path + '/sources'

        # unzip to folder_path
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(sources)

        #2.- setup sources in config file - in order to prepare this for future things...
        self.cfg.set("JUDAS", "sources_folder", sources)

        #3.- calculate context
        # genera context
        results = self.cfg.get("JUDAS", "results_folder")
        self.context = eatj.Context(results)
        # list of files to be processed
        files_to_process = ["%s/%s" % (sources, x) for x in os.listdir(sources)]
        self.context.createContextFromJson(files_to_process)
        """
        saved = self.context.save_context(eatj.Context.getDefaultFilePath())
        if not saved:
            self.error('Context not saved in %s' % eatj.Context.getDefaultFilePath())

        #3.- return context processed
        with open (eatj.Context.getDefaultFilePath(), 'r') as fileresult:
            data = fileresult.readlines()

        #Report funcion is defined in cortexutils3.analyzer e.g. empty: self.report({'results': self.getData()})
        self.report({'results':data})
        """
        self.report({'results':self.context.__str__()})


    def summary(self, raw: dict) -> dict:
        """The summary is used for the short templates.

        :param raw: The raw result dictionary.
        :returns:   a maybe shortened dictionary for the short templates directly under the observable header. If this is
                    a list and not a dict, TheHive won't display any short-reports."""
        return raw


if __name__ == '__main__':
    """This is necessary, because it is called from the CLI."""
    JudasAnalyzer().run()

