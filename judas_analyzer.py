# ref: https://cert-bund-cortex-analyzers.readthedocs.io/en/latest/_modules/example_analyzer.html#MinimalPythonAnalyzer
from cortexutils.analyzer import Analyzer

import auxiliar.auxiliar as aux
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


    def run(self):
        """This is called when running the class, as you can see at the __main__ part below. Remember to always report a
        python dictionary. """
        # get config
        self.cfg = getConf()

        #1.- get parameters
        if self.data_type == "file":
            filepath = self.get_param("file")
            # check if is a zip or a json file
            if aux.checkExtension(filepath, ['zip','json']):
                folder_path = os.path.dirname(os.path.abspath(filepath))
                aux.createFolder('aux', folder_path)
                folder_path = folder_path + '/aux'

                if aux.checkExtension(filepath, ['json']):
                    # move to new folder
                    shutil.move(filepath, folder_path)
                else:
                    # unzip to folder_path
                    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
                        zip_ref.extractall(folder_path)
            else:
                self.error('Wrong data type, expected zip or json')

        #2.- setup sources in config file - not needed really, but in order to prepare this for future thins...
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

