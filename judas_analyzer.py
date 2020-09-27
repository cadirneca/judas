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
import shutil
import zipfile
import os

class JudasAnalyzer(Analyzer):
    """This is the analyzer for JUDAS, please take into account that this only adds the feature for analysing JSON
       files"""

    def __init__(self):
        """Initialization of the class. Here normally all parameters are read using `self.get_param`
        (or `self.getParam`)"""
        Analyzer.__init__(self)
        self.filepath = self.get_param("file", None, None)
        self.iszip = aux.checkExtension(self.filepath, ['zip'])
        self.isjson = aux.checkExtension(self.filepath, ['json'])

    def run(self):
        """This is called when running the class, as you can see at the __main__ part below. Remember to always report a
        python dictionary. """
        # get config
        self.cfg = getConf()

        #1.- get parameters
        if self.iszip or self.isjson:
            folder_path = self.get_param("file")
            aux.createFolder('aux', folder_path)
            folder_path = folder_path + '/aux'

            if self.iszip or self.isjson:
                folder_path = os.path.dirname(os.path.abspath(self.filepath))
                aux.createFolder('aux', folder_path)
                folder_path = folder_path + '/aux'

                if self.isjson:
                    # move to new folder
                    shutil.move(self.filepath, folder_path)
                    self.filepath = folder_path + os.path.basename(self.filepath)
                else:
                    # unzip to folder_path
                    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
                        zip_ref.extractall(folder_path)
            else:
                self.error('Wrong data type, expected zip or json')

        #2.- setup sources in config file - in order to prepare this for future thins...
        self.cfg.set("JUDAS", "sources_folder", folder_path)

        #3.- calculate context
        # genera context
        self.context = eatj.Context(eatj.Context(self.cfg.get("JUDAS", "context_folder")))
        # list of files to be processed
        files_to_process = os.listdir(folder_path)
        self.context.createContextFromJson(files_to_process)
        self.context.save_context(eatj.Context.getdefaultfile())

        #3.- return context processed

        #Report funcion is defined in cortexutils3.analyzer e.g. empty: self.report({'results': self.getData()})
        self.report({'results':eatj.Context.getdefaultfile()})


    def summary(self, raw: dict) -> dict:
        """The summary is used for the short templates.

        :param raw: The raw result dictionary.
        :returns:   a maybe shortened dictionary for the short templates directly under the observable header. If this is
                    a list and not a dict, TheHive won't display any short-reports."""
        return raw


if __name__ == '__main__':
    """This is necessary, because it is called from the CLI."""
    JudasAnalyzer().run()

