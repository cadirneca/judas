# -------
# JUDAS. JSON Users and Devices AnalySys tool
# -------
# @author:      Ana Nieto
# @country:     Spain
# @website:     https://www.linkedin.com/in/ananietojimenez/
######

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import *
from tkinter.ttk import Combobox

import json
import os
from PIL import Image  # pip install Pillow
import datetime
from ju_eaters import eatingNetwork as eatn, eatingJson as eatj, eating as eat
import ntpath
import shodan
import pipl
from auxiliar import auxiliar
from auxiliar.external import ipinfo

import matplotlib
matplotlib.use("TkAgg") # this is for Mac OS

# configuration parameters are loaded using getConf
from auxiliar.external.thehive.common import getConf
# using configparser to build context.json
from configparser import ConfigParser
# using the official types for observable:
from ju_feeders.feedTheHive import JudasConnector
# connect with thehive:
from ju_feeders.feedTheHive import connectJudas



class Judas(Frame):

    FILES = 'FILES'
    CONTEXT = 'CONTEXT'
    NETWORK = "CONTEXT_NOTIFY" #'NETWORK'
    CONTEXT_NOTIFY = "CONTEXT_NOTIFY"

    API = 'API'
    REPORT = 'REPORT'
    GRAPH_MODE0 = ".gif(Summary)"
    GRAPH_MODE1 = "Web(All)"
    GRAPH_MODE2 = "Both"

    def __init__(self):
        # Init configuration values:
        self.cfg = getConf()

        # Init variables:
        self.initVariables()

        # Init frame:
        Frame.__init__(self)

        #self.rowconfigure(1, weight=1)
        #self.columnconfigure(1, weight=1)

        self.master.title("JSON Users and Devices AnalysiS tool")
        #self.master.rowconfigure(0, weight=1)
        #self.master.columnconfigure(0, weight=1)
        img = tk.Image("photo", file=self.cfg.get('JUDAS', 'icon'))
        self.master.tk.call('wm', 'iconphoto', self.master._w, img)

        #self.master.geometry("815x700")
        #icon_path = os.getcwd() + '/judas.ico'
        #self.master.wm_iconphoto(True, PhotoImage(file=icon_path))
        self.grid(sticky=W + E + N + S)
        self.master.resizable()

        # Notebook
        self.notebook = ttk.Notebook(self.master)
        self.frameFiles = Frame(self.notebook)      # frame to handle files
        self.frameContext = Frame(self.notebook)    # frame to handle the context
        self.frameAPIs = Frame(self.notebook)    # frame to handle the context
        self.frameReport = Frame(self.notebook)    # frame to handle the context
        self.frameEmail = Frame(self.notebook)    # frame to handle the context
        self.frameNetwork = Frame(self.notebook)    # frame to handle the context
        self.frameMemory = Frame(self.notebook)  # frame to handle the context

        # Initialize Tab for Context:
        self.setup_frame_for_context() # Initialize self.frameContext

        # Initialize Tab for Files:
        self.setup_frame_for_files() # Initialize self.frameFiles -- not until the context has been loaded

        # Initialize Tab for API Keys:
        self.setup_frame_for_APIKeys() # Initialize self.frameAPIs

        # Initialize Tab for Report:
        self.setup_frame_for_Report()  # Initialize self.frameReport

        # Initialize Tab for Network:
        #self.setup_frame_for_Network()  # Initialize self.frameNetwork

        # Initialize Tab for Email:
        #self.setup_frame_for_Email()  # Initialize self.frameEmail

        # Initialize Tab for Memory:
        #self.setup_frame_for_Memory()  # Initialize self.frameMemory

        # Rest of configurations:
        self.notebook.add(self.frameContext, text="Context")
        self.notebook.add(self.frameFiles, text="Files")
        #self.notebook.add(self.frameNetwork, text="Network")
        #self.notebook.add(self.frameEmail, text="Email")
        #self.notebook.add(self.frameMemory, text="Memory")
        self.notebook.add(self.frameAPIs, text="API Keys")
        self.notebook.add(self.frameReport, text="Report")

        self.notebook.pack(expand=True)
        self.pack(expand=True)

        # First state:
        self.initState()

    def __del__(self):
        # stop the http server (if opened)
        if self.http_handler is not None:
            self.http_handler.stop()


    # ----------------
    # GUI Elements
    # ----------------
    def initVariables(self):
        # Initialise parameter for files
        self.filePaths = {}
        # Initialise parameter for context
        self.context = None
        # Handler to the http server (graph)
        self.http_handler = None
        # API for Shodan
        self.apiShodan = None
        # Network:
        self.initializeNetwork()


    def initFrameFileSelection(self, myframe):
        # Panel to select type of files
        self.frameFileType = Frame(myframe)
        self.frameFileType.grid(sticky=N+S+E+W)

        self.varJson = IntVar()
        self.varJson.set(1)
        self.checkJson = Checkbutton(self.frameFileType, text=".json", variable=self.varJson, \
                                     onvalue = 1, offvalue = 0, height=5, \
                                     width = 20)
        self.checkJson.grid(row=0, column=0, sticky=N + S + E + W)
        self.varPcap = IntVar()
        self.varPcap.set(1)
        self.checkPcap= Checkbutton(self.frameFileType, text=".pcap", variable=self.varPcap, \
                                    onvalue=1, offvalue=0, height=5, \
                                    width=20)
        self.checkPcap.grid(row=0, column=2, sticky=N + S + E + W)
        self.listofckecks = [self.varJson, self.varPcap]

        self.button2 = Button(self.frameFileType, text="Feed", bg='deep sky blue', command=self.getRelevantFiles)
        self.button2.grid(row=0, column=3, columnspan=3, sticky=N + S + E + W)

        return self.frameFileType

    def build_table_files(self, parent):
        """
        :param parent: parent to allocate the table (e.g. frame)
        :return: frame with the table
        """
        if self.context is None:
            files = []
        else:
            files = auxiliar.File.getFiles(self.context.getFilesProcessed())
            self.writeText4("Loading files included in the current context.")

        return auxiliar.File.getTable(parent, files)

    def update_table_files(self):
        self.scroll_table = self.build_table_files(self.frameFiles)
        self.scroll_table.grid(row=0, columnspan=2, sticky=W+E+N+S)

    def setup_frame_for_files(self):
        #self.frameFiles.grid(sticky=W+E+N+S)

        # create table to show files
        self.update_table_files()

        # BUTTONS
        self.panedBottomFile = PanedWindow(self.frameFiles, orient=HORIZONTAL)
        self.panedBottomFile.grid_propagate(False)

        self.labelKeyFile = Label(self.panedBottomFile, text="Keywords:")
        self.entryKeywordFile = Entry(self.panedBottomFile)#, width=50)
        self.entryKeywordFile.insert(INSERT, " ")
        self.button5 = Button(self.panedBottomFile, text="Search", command=self.searchKeywordsFile)

        self.panedBottomFile.add(self.labelKeyFile)
        self.panedBottomFile.add(self.entryKeywordFile)
        self.panedBottomFile.add(self.button5)

        self.panedBottomFile.grid(row=1, columnspan=2, sticky=W+E)

        # TAG FOR RESULTS
        self.label_text7 = StringVar()
        self.label_text7.set('Results:')
        self.label7 = Label(self.frameFiles, textvariable=self.label_text7, justify=CENTER, anchor=W)
        self.label7.grid(row=2, columnspan=2, sticky=W + E)
        self.label7.grid_propagate(False)

        # RESULTS
        self.panedBottomFileErrors = PanedWindow(self.frameFiles, orient=HORIZONTAL)
        self.panedBottomFileErrors.grid(row=3, columnspan=2, padx=275, sticky=W+E)
        self.panedBottomFileErrors.grid_propagate(False)

        self.text4 = Text(self.panedBottomFileErrors, background='snow')  # , wrap = NONE)
        self.text4.insert(INSERT, '\n')  # lorem.paragraph())
        self.text4.config(state=DISABLED)  # only for read

        self.scrollbar4 = Scrollbar(self.panedBottomFileErrors, orient=VERTICAL, command=self.text4.yview)
        self.scrollbar4.pack(side=RIGHT, fill=Y)
        #self.text4['yscroll'] = self.scrollbar4.set


        self.text4.pack(side=LEFT, fill="both", expand=True)

        #self.frameFiles.pack(expand=True)

    def setup_frame_for_context(self):

        # LEFT:
        self.panedResults = PanedWindow(self.frameContext, orient=VERTICAL)  # , background='sky blue')

        self.label_text5 = StringVar()
        self.label_text5.set('Results:')
        self.label5 = Label(self.panedResults, textvariable=self.label_text5, justify=CENTER, anchor=W)
        self.text2 = Text(self.panedResults, background='alice blue', width=100)
        self.text2.insert(INSERT, "")

        self.scrollbar2 = Scrollbar(self.panedResults, orient=VERTICAL, command=self.text2.yview)
        self.text2['yscroll'] = self.scrollbar2.set
        self.button14_1 = Button(self.panedResults, text="Save Results (plain text)", bg='blue', command=self.save_results)
        self.button14_2 = Button(self.panedResults, text="Send Observables to TheHive", bg='blue', command=self.save_observable_context)

        self.panedResults.add(self.label5)
        self.panedResults.add(self.text2)
        self.panedResults.add(self.button14_1)
        self.panedResults.add(self.button14_2)

        self.panedResults.grid(row=0, column=0, columnspan=2, sticky=W + E + N + S)


        # RIGHT:
        self.panedButtons = PanedWindow(self.frameContext, orient=VERTICAL)  # , background='sky blue')

        # Default folder
        self.label_text10 = StringVar()
        self.label_text10.set('Default folder:')
        self.label10 = Label(self.panedButtons, textvariable=self.label_text10, justify=CENTER, anchor=W)
        self.frame_options = Frame(self.panedButtons)
        self.frame_options.grid(sticky=N + S + E + W)
        self.initLabelText_sourceFolder()
        self.label = Label(self.frame_options, textvariable=self.label_text, wraplength=700, justify=LEFT, anchor=W)
        self.label.grid(row=0, column=0, sticky=N + S + E + W)
        self.label.config(fg='blue')
        self.button1 = Button(self.frame_options, text="Change", command=self.selectandloadcontext)
        self.button1.grid(row=0, column=1, sticky=N+S+E+W)

        # Files used tu build the context
        self.label_text9 = StringVar()
        self.label_text9.set('Type of file added:')
        self.label9 = Label(self.panedButtons, textvariable=self.label_text9, justify=CENTER, anchor=W)
        self.initFrameFileSelection(self.panedButtons)

        # Show context
        self.button3 = Button(self.panedButtons, text="Show JUDAS context", bg='deep sky blue',command=self.showContext)

        #graphs:
        self.pannedGraph = PanedWindow(self.panedButtons, orient=HORIZONTAL)
        self.comboGraph = Combobox(self.pannedGraph, state="readonly", values=(self.GRAPH_MODE0, self.GRAPH_MODE1,
                                                                               self.GRAPH_MODE2))
        self.comboGraph.set(self.GRAPH_MODE1)
        #self.comboGraph["values"] = [".gif image", "Web", "Both"]
        self.button9 = Button(self.pannedGraph, text="Plot", bg='deep sky blue', command=self.showContextGraph)
        self.pannedGraph.add(self.comboGraph)
        self.pannedGraph.add(self.button9)

        self.label_text2 = StringVar()
        self.label_text2.set('Operations:')
        self.label2 = Label(self.panedButtons, textvariable=self.label_text2, justify=CENTER, anchor=W)
        self.button8 = Button(self.panedButtons, text="Show relationships", bg='deep sky blue',command=self.showContextGraph)
        self.button6 = Button(self.panedButtons, text="Summary", bg='yellow',command=self.summary)
        self.button10 = Button(self.panedButtons, text="Show IDs", bg='yellow',command=self.showidcontext)
#        self.label_text3 = StringVar()
#        self.label_text3.set('Network:')
#        self.label3 = Label(self.panedButtons, textvariable=self.label_text3, justify=CENTER, anchor=W)
#        self.button12 = Button(self.panedButtons, text="Show network info", bg='yellow', command=self.showNetworkInfo)
#        self.button13 = Button(self.panedButtons, text="Acquire Public IP info", bg='yellow',command=self.searchInfoPublicIP)
#        self.button15 = Button(self.panedButtons, text="Correlate with context", bg='blue',command=self.correlate_network)
#        self.button16 = Button(self.panedButtons, text="Add to context", bg='blue',
#                               command=self.addNetworkToContext)
        self.label_text8 = StringVar()
        self.label_text8.set('Acquire public info (OSINT):')
        self.label8 = Label(self.panedButtons, textvariable=self.label_text8, justify=CENTER, anchor=W)
        self.button17 = Button(self.panedButtons, text="Users", bg='yellow',command=self.searchUsersPublicInfo)
        self.button18 = Button(self.panedButtons, text="Devices", bg='yellow',command=self.searchDevicePublicInfo)
        self.button13 = Button(self.panedButtons, text="Network", bg='yellow',command=self.searchInfoPublicIP)

        # self.panedButtons.add(self.button4)
        self.panedButtons.add(self.label10)
        self.panedButtons.add(self.frame_options)
        self.panedButtons.add(self.label9)
        self.panedButtons.add(self.frameFileType)
        self.panedButtons.add(self.button3)
        self.panedButtons.add(self.pannedGraph)
        self.panedButtons.add(self.label2)
        self.panedButtons.add(self.button6)
        self.panedButtons.add(self.button10)
        #self.panedButtons.add(self.label3)
        #self.panedButtons.add(self.button12)
        #self.panedButtons.add(self.button13)
        #self.panedButtons.add(self.button15)
        #self.panedButtons.add(self.button16)
        self.panedButtons.add(self.label8)
        self.panedButtons.add(self.button17)
        self.panedButtons.add(self.button18)
        self.panedButtons.add(self.button13)
        self.panedButtons.grid(row=0, column=2, sticky=W + E + N + S)

        # BOTTOM
        self.panedBottom = PanedWindow(self.frameContext, orient=HORIZONTAL)

        self.labelKey = Label(self.panedBottom, text="Keywords:")
        self.entryKeyword = Entry(self.panedBottom, width=50)
        self.entryKeyword.config(fg='blue')
        self.entryKeyword.insert(INSERT, "")
        self.button5 = Button(self.panedBottom, text="Search", command=self.searchKeywords)

        self.panedBottom.add(self.labelKey)
        self.panedBottom.add(self.entryKeyword)
        self.panedBottom.add(self.button5)
        self.panedBottom.grid(row=1, columnspan=3, sticky=W + E + N + S)

        # - errors and warnings
        self.label_notifications = Label(self.frameContext, text="Notifications:")
        self.label_notifications.grid(column=0, row=2)#, sticky=W + E + N + S)

        self.panedEWContext = PanedWindow(self.frameContext, orient=VERTICAL)

        self.text3 = Text(self.panedEWContext, background='snow' , width=10,height=10)#, wrap = NONE)
        self.text3.insert(INSERT, '\n')  # lorem.paragraph())
        self.text3.config(state=DISABLED)  # only for read

        self.scrollbar3 = Scrollbar(self.panedEWContext, orient=VERTICAL, command=self.text3.yview)
        self.scrollbar3.pack(side="right", fill="y", expand=False)

        self.text3.pack(side="left", fill="both", expand=True)


        self.panedEWContext.grid(row=3, columnspan=3, sticky=W + E + N + S)

        self.frameContext.pack()


    def setup_frame_for_APIKeys(self):

        self.frameAPIs.grid(sticky=N + S + E + W)

        # 0 - Buttons for load/save API keys
        self.labelKeyInfo = Label(self.frameAPIs, text="Configure default API keys in judas.conf")
        self.labelKeyInfo.grid(column=0, row=0, sticky=E+W)
        self.buttonReloadAPI = Button(self.frameAPIs, text="Reload", command=self.refreshAPIkeys)
        self.buttonReloadAPI.grid(column=1, row=0, sticky=E+W)

        # 1 - Network info
        self.labelNetworkInfo = Label(self.frameAPIs, text="NETWORK")
        self.labelNetworkInfo.grid(column=0, row=1, columnspan=2,  sticky=E + W)

        # VirusTotal
        self.labelVT = Label(self.frameAPIs, text="VirusTotal API Key:")
        self.labelVT.grid(column=0, row=2)
        self.entryVT = Entry(self.frameAPIs, width=100)
        self.entryVT.grid(column=1, row=2, sticky=E + W) #, columnspan=3

        # PassiveTotal
        self.labelPT = Label(self.frameAPIs, text="Passive Total API Key:")
        self.labelPT.grid(column=0, row=3)
        self.entryPT = Entry(self.frameAPIs, width=100)
        self.entryPT.grid(column=1, row=3, sticky=E + W)

        # 2 - Devices
        self.labelNetworkInfo = Label(self.frameAPIs, text="DEVICES")
        self.labelNetworkInfo.grid(column=0, row=4, columnspan=2,  sticky=E + W)

        # Shodan
        self.labelShodan = Label(self.frameAPIs, text="Shodan API Key:")
        self.labelShodan.grid(column=0, row=5)
        self.entryShodan = Entry(self.frameAPIs, width=100)
        self.entryShodan.grid(column=1, row=5,  sticky=E + W)

        # 3 - Users
        self.labelNetworkInfo = Label(self.frameAPIs, text="USERS")
        self.labelNetworkInfo.grid(column=0, row=6, columnspan=2,  sticky=E + W)
        # Pipl
        # - Business
        self.labelPiplBus = Label(self.frameAPIs, text="Pipl API Key Business:")
        self.labelPiplBus.grid(column=0, row=7)
        self.entryPiplBus = Entry(self.frameAPIs, width=100)
        self.entryPiplBus.grid(column=1, row=7, sticky=E + W)
        # - Social
        self.labelPiplSoc = Label(self.frameAPIs, text="Pipl API Key Social:")
        self.labelPiplSoc.grid(column=0, row=8)
        self.entryPiplSoc = Entry(self.frameAPIs, width=100)
        self.entryPiplSoc.grid(column=1, row=8, sticky=E + W)
        # - Contact
        self.labelPiplCon = Label(self.frameAPIs, text="Pipl API Key Contact:")
        self.labelPiplCon.grid(column=0, row=9)
        self.entryPiplCon = Entry(self.frameAPIs, width=100)
        self.entryPiplCon.grid(column=1, row=9, sticky=E + W)

        self.frameAPIs.pack()

        #Load default API keys from judas.conf
        self.loadAPIkeys()

    def setup_frame_for_Report(self):

        self.frameReport.grid(sticky=N + S + E + W)

        self.panelog = Frame(self.frameReport)#PanedWindow(self.frameReport, orient=HORIZONTAL, bg='deep sky blue')
        self.panelog.grid(sticky=N + S + E + W)
        self.button7 = Button(self.panelog, text="Save Report", bg='deep sky blue', command=self.save_logs)
        self.button7.grid(row=0, column=1, sticky=E + W)
        self.button4 = Button(self.panelog, text="Clear Report", bg='deep sky blue', command=self.clearText1)
        self.button4.grid(row=0, column=0, sticky=E + W)

        self.panelog.pack(side="top", fill="x")

        self.text1 = Text(self.frameReport, background='snow')  # , wrap = NONE)
        self.text1.insert(INSERT, '\n')  # lorem.paragraph())
        self.text1.config(state=DISABLED)  # only for read

        self.scrollbar = Scrollbar(self.frameReport, orient=VERTICAL, command=self.text1.yview)
        self.text1['yscroll'] = self.scrollbar.set

        self.scrollbar.pack(side="right", fill="y")
        self.text1.pack(side="left", fill="both", expand=True)


        self.frameReport.pack(side="top", fill="x")


    def setup_frame_for_Network(self):
        self.frameNetwork.grid(sticky=N + S + E + W)

        #self.paneNetwork = Frame(self.frameNetwork)  # PanedWindow(self.frameReport, orient=HORIZONTAL, bg='deep sky blue')
        #self.paneNetwork.grid(sticky=N + S + E + W)

        self.panedButtonsNet = Frame(self.frameNetwork)  # PanedWindow(self.frameReport, orient=HORIZONTAL, bg='deep sky blue')
        self.panedButtonsNet.grid(sticky=N + S + E + W)

        self.label3 = Label(self.panedButtonsNet, text="Network:")
        self.label3.grid(column=0, row=0, sticky=E + W)

        self.button24 = Button(self.panedButtonsNet, text="Select file (.pcap)", bg='yellow',
                               command=self.loadNetwork)
        self.button12 = Button(self.panedButtonsNet, text="Show network info", bg='yellow',
                               command=self.showNetworkInfo)
        self.button12.grid(column=0,row=1, sticky=E + W)

        #self.button13 = Button(self.panedButtonsNet, text="Acquire Public IP info", bg='yellow',
        #                       command=self.searchInfoPublicIP)
        #self.button13.grid(column=0, row=2, sticky=E + W)

        self.button15 = Button(self.panedButtonsNet, text="Correlate with context", bg='blue',
                               command=self.correlate_network)
        self.button15.grid(column=0, row=3, sticky=E + W)

        self.button16 = Button(self.panedButtonsNet, text="Add to context", bg='blue',
                               command=self.addNetworkToContext)
        self.button16.grid(column=0, row=4, sticky=E + W)


        # text
        self.panedFeedbackNet = PanedWindow(self.frameNetwork, orient=VERTICAL)

        self.textnetwork = Text(self.panedFeedbackNet, background='snow')  # , wrap = NONE)
        self.textnetwork.insert(INSERT, '\n')  # lorem.paragraph())
        self.textnetwork.config(state=DISABLED)  # only for read

        self.scrollbar5 = Scrollbar(self.panedFeedbackNet, orient=VERTICAL, command=self.textnetwork.yview)
        self.textnetwork['yscroll'] = self.scrollbar5.set

        self.scrollbar5.pack(side="right", fill="y")
        self.textnetwork.pack(side="left", fill="both", expand=True)

        self.panedFeedbackNet.grid(row=5, sticky=N + S + E + W)

        self.frameNetwork.pack()


    def setup_frame_for_Email(self):
        self.frameEmail.grid(sticky=N + S + E + W)

        self.paneEmail = Frame(self.frameEmail)  # PanedWindow(self.frameReport, orient=HORIZONTAL, bg='deep sky blue')
        self.paneEmail.grid(sticky=N + S + E + W)

        self.paneEmail.pack()


        self.frameEmail.pack()


    def setup_frame_for_Memory(self):
        self.frameMemory.grid(sticky=N + S + E + W)

        self.panedButtonsMemory = Frame(self.frameMemory)
        self.panedButtonsMemory.grid(sticky=N + S + E + W)

        self.label3 = Label(self.panedButtonsMemory, text="Memory:")
        self.label3.grid(column=0, row=0, sticky=E + W)

        self.button18 = Button(self.panedButtonsMemory, text="List processes", bg='yellow',
                               command=self.showMemoryProcesses)
        self.button18.grid(column=0, row=1, sticky=E + W)

        self.button19 = Button(self.panedButtonsMemory, text="Show connections", bg='yellow',
                               command=self.searchInfoPublicIP)
        self.button19.grid(column=0, row=2, sticky=E + W)

        self.button22 = Button(self.panedButtonsMemory, text="Search for public IPs", bg='yellow',
                               command=self.searchInfoPublicIP)
        self.button22.grid(column=0, row=3, sticky=E + W)

        self.button23 = Button(self.panedButtonsMemory, text="Extract item from memory", bg='yellow',
                               command=self.extractItemMemory)
        self.button23.grid(column=0, row=4, sticky=E + W)

        self.button20 = Button(self.panedButtonsMemory, text="Correlate with context", bg='blue',
                               command=self.correlate_memory)
        self.button20.grid(column=0, row=5, sticky=E + W)

        self.button21 = Button(self.panedButtonsMemory, text="Add to context", bg='blue',
                               command=self.addMemoryToContext)
        self.button21.grid(column=0, row=6, sticky=E + W)

        self.frameNetwork.pack(expand=True)


    def showMemoryProcesses(self):
        return 0

    def searchInfoPublicIP(self):
        return 0

    def extractItemMemory(self):
        return 0

    def correlate_memory(self):
        return 0

    def addMemoryToContext(self):
        return 0

    # ----------------
    # AUXILIAR
    # ----------------
    def getTime(self):
        return datetime.datetime.today().time().isoformat()

    def getDate(self):
        return datetime.datetime.today().date().isoformat()

    def getLogs(self):
        return self.text1.get('1.0', 'end')

    def getResults(self):
        return self.text2.get('1.0', 'end')

    def browse_button(self):
        global folder_path
        filename = filedialog.askdirectory() #askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))#

        if filename is not None and len(filename)>0:
            self.label_text.set(filename)
        else:
            self.writeWarning('Folder not selected', Judas.FILES)

    def browse_button_file(self):
        global file_path
        filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pcap files","*.pcap"),("all files","*.*")))#

        if filename is not None and len(filename)>0:
            self.setLabel4(filename)
        else:
            # Default .pcap file
            self.writeWarning('File not selected. Loading default file...', Judas.FILES)
            self.initLabelText4()

    def save_file_as(self, text, defextension='.txt', dialog = True):
        default = ""
        if dialog:
            self.filename = filedialog.asksaveasfilename(defaultextension=defextension)#, filetypes=self._filetypes)
        else:
            self.filename = self.context.getDefaultFilePath()
            default = "default"
        # delete file if exists
        if os.path.exists(self.filename): os.remove(self.filename)

        self.write("File %s saved in %s location" % (self.filename, default), Judas.CONTEXT_NOTIFY)

        if self.filename is not None and len(self.filename)>0:
            f = open(self.filename, 'w')
            f.write(text)
            f.close()
            if dialog: messagebox.showinfo('JSON Users and Devices AnalysyS tool', 'File Saved')

    def save_logs(self):
        self.save_file_as(self.getLogs())

    def save_results(self):
        self.save_file_as(self.getResults())

    def save_observable_context(self, other = True, datamin=5):
        """
        :param other: if True this method will add any observable, even if this is not defined in TheHive
        :param datamin: determine min length (characters) of data to be considered observable
        :return: this method will contact with TheHive (see judas.conf) to send observables
        """
        # observables:
        # we are going to use the .txt file created when the context is saved
        # and then build the observables
        context_file_name = "context.json"

        if self.cfg.get("TheHive", "enable") != "True":
            self.writeError('Please, enable TheHive in judas.conf', Judas.CONTEXT_NOTIFY)
            return False

        # write the context just as it is shown
        contPath = self.context.getDefaultFilePath()
        self.write("Writing context:" + contPath, Judas.CONTEXT_NOTIFY)
        self.save_file_as(self.getResults(), dialog=False)

        # convert to get the observables
        self.write("Convert context to %s with observables" % context_file_name, Judas.CONTEXT_NOTIFY)
        title = "JUDAS Context " + self.getDate() + " "+ self.getTime()
        description = "Alexa logs"
        tags = ['JUDAS', 'Alexa', 'JSON', 'DFIR']
        data = {"title":title,
                "tags":tags,
                "observables":[]}
        observables = []
        confred = ConfigParser()
        contPath = self.context.RESULTS_FOLDER + "/" +context_file_name
        try:
            confred.read(self.context.getDefaultFilePath())
            nobjects = len(confred.sections())
            self.write("Objects to be procesed:%d" % nobjects, Judas.CONTEXT_NOTIFY)
            description += " - %d objects generated" % nobjects
            # now load observables
            observable_types = JudasConnector.OB_EQUIVALENCE.keys()

            for section in confred.sections():
                # each section is a object in the context, with a class and a id
                myclass = confred.get(section, "class")
                myid = confred.get(section, "id")
                # each section is a ID
                options = confred.options(section)
                # remove class from options
                options.remove("class")
                # add options/properties as observables
                for op in options:
                    ot = JudasConnector.getObservableTypeEquivalence(op)

                    if ot != JudasConnector.OB_OTHER:
                        # perfect:
                        odata = confred.get(section, ot)
                        new_o = {"data": odata, "dataType": ot, "comment": section,
                                 "tags": [myclass, myid], "tlp":2}
                        if len(odata) > datamin: observables += [new_o]
                    elif other: # other is allowed as a type, add all the options available as other:
                        for op in options:
                            if op in ["id", "email"]: tlp=3
                            elif op in ["type"]: tlp:2
                            else: tlp = 2
                            odata = confred.get(section, op)
                            new_o = {"data": odata, "dataType": ot, "comment": section,
                                     "tags": [op, myclass, myid], "tlp":tlp}
                            if len(odata) > datamin: observables += [new_o]

            # add the context in plain text as observable
            observables += [{"data":self.context.getDefaultFilePath(),
                             "dataType": JudasConnector.OB_FILE,
                             "comment": "JUDAS Context",
                             "tags": ['JUDAS','context']}]

            # add network data as observable:
            ip_list = self.getIPs() # this is not working due a problem with pyshark in eatingNetwork.py
            if ip_list is None or len(ip_list)==0:
                self.writeWarning('Network not available, check path in judas.conf', window=Judas.CONTEXT_NOTIFY)
            npri = 0
            npu = 0
            for ip in ip_list:
                if ipinfo.ispublic(ip):
                    comment = "public"
                    tlp = 1
                    tags = [ip, 'public']
                    npu += 1
                else:
                    comment = "private"
                    tlp = 2
                    tags = [ip,'private']
                    npri += 1
                new_o = {"data": ip, "dataType": JudasConnector.OB_IP, "comment": comment,
                            "tags": tags, "tlp":tlp}
                observables += [new_o]

            #description += " , %d public ip and %s private ip" % (npu, npri)

            data.update({"observables":observables, "description":description})

            # save as json
            if os.path.exists(contPath): os.remove(contPath)
            with open(contPath, 'w') as fp:
                json.dump(data, ensure_ascii=False, fp=fp)

            # call thehive to send the context:
            connectJudas(contPath)

        except Exception as e:
            #logger.error('%s', __name__, exc_info=True)
            msg = 'writing observables, exception: %s' % (e)
            self.writeError(msg, Judas.CONTEXT)


    def openImage(self, filename, title="judas context graph"):
        img = Image.open(filename)
        img.show()
        """
        nwin = Toplevel()
        nwin.title(title)

        image = Image.open(filename)#os.getcwd()+"/"+filename)
        photo = ImageTk.PhotoImage(image)
        lbl2 = Label(nwin, image=photo)
        lbl2.img = photo
        lbl2.pack()
        nwin.mainloop()
        """

    def saveAPIkeys(self, file='apiKeys.json'):
        """ Save a file with the API keys"""

        dicto = {"shodan":self.entryShodan.get(), "piplsoc":self.entryPiplSoc.get(), "piplcon":self.entryPiplCon.get(),
                 "piplbus":self.entryPiplBus.get(), "VirusTotal":self.entryVT.get(), "PassiveTotal":self.entryPT.get()}
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".json")#
            with open(filename, 'w') as fp:
                json.dump(dicto, fp)

            return True
        except:
            return False

    def refreshAPIkeys(self):
        """ refresh API keys from judas.conf"""
        self.cfg = getConf()

        self.entryVT.delete('0', END)
        self.entryPT.delete('0', END)
        self.entryShodan.delete('0', END)
        self.entryPiplBus.delete('0', END)
        self.entryPiplSoc.delete('0', END)
        self.entryPiplCon.delete('0', END)
        self.loadAPIkeys()

    def loadAPIkeys(self):
        """ Loads API keys from judas.conf"""

        # insert data
        self.entryVT.insert(INSERT, self.cfg.get('OSINT', 'VirusTotal'))
        self.entryPT.insert(INSERT, self.cfg.get('OSINT', 'PassiveTotal'))
        self.entryShodan.insert(INSERT, self.cfg.get('OSINT', 'Shodan'))
        self.entryPiplBus.insert(INSERT, self.cfg.get('OSINT', 'PiplBusiness'))
        self.entryPiplSoc.insert(INSERT, self.cfg.get('OSINT', 'PiplSocial'))
        self.entryPiplCon.insert(INSERT, self.cfg.get('OSINT', 'PiplContact'))
        return True


    #----------------
    # GET ELEMENTS OF THE GUI
    #----------------
    def getAPIkeyVT(self):
        """
        :return: API key for VirusTotal (if any)
        """
        return self.entryVT.get()

    def getAPIkeyPipl(self, mode=0):
        """
        :param mode: if 0 (default) returns a list with all API keys in this order: Social, Contact, Business.
        If 1 returns a list with a single API Key for social, if 2 a single key for contact and if 3 a single key for
        business
        :return: Gets the API keys for Pipl (if any)
        """
        if mode==0:
            return [self.entryPiplSoc.get(), self.entryPiplCon.get(), self.entryPiplBus.get()]
        elif mode==1:
            return [self.entryPiplSoc.get()]
        elif mode==2:
            return [self.entryPiplCon.get()]
        elif mode==3:
            return [self.entryPiplBus.get()]

    def getAPIkeyShodan(self):
        """
        :return: API key for shodan (if any)
        """
        return self.entryShodan.get()

    def getPath(self):
        return self.label_text.get()

    def getPathNetwork(self):
        return self.label_text4.get()

    def getKeywordsList(self):
        words = self.entryKeywordFile.get()

        if words is None:
            return []

        lwords = words.replace(' ','').split(',')
        if len(lwords)==1 and len(lwords[0])==0:
            return []

        else:
            return lwords

    # ----------------
    # INITIALISE ELEMENT
    # ----------------
    def initState(self):
        self.writeLog('Date:' + self.getDate())

        res = self.extractContext(False)
        if res:
            self.writeLog('Default context loaded from %s' % self.getPath())
            #initialize table for files
            self.update_table_files()
        else:
            self.writeLog('Warning!! Default context not loaded...')

        # Initialise Network Parameters
        #self.initializeNetwork()



    def initLabelText_sourceFolder(self):
        self.label_text = StringVar()
        # try to get 'source' local folder complete path (absolute):
        self.label_text.set(self.cfg.get("JUDAS", "sources_folder"))
        self.is_directory = True


    def setLabel4(self, path):
        self.label_text4.set(path)

    def initLabelText4(self):
        self.label_text4 = StringVar()
        self.setLabel4(self.cfg.get("JUDAS", "network_file"))

    def clearText1(self):
        self.text1.config(state=NORMAL)
        self.text1.delete('1.0', END)
        self.text1.insert(INSERT, '')
        self.text1.config(state=DISABLED)

        self.writeLog('Date:' + self.getDate())

    def clearText2(self):
        #self.text2.config(state=NORMAL)
        self.text2.delete('1.0', END)
        self.text2.insert(INSERT, '')
        #self.text2.config(state=DISABLED)

    def clearText3(self):
        self.text3.config(state=NORMAL)
        self.text3.delete('1.0', END)
        self.text3.insert(INSERT, '')
        self.text3.config(state=DISABLED)

    def clearText4(self):
        self.text4.config(state=NORMAL)
        self.text4.delete('1.0', END)
        self.text4.insert(INSERT, '')
        self.text4.config(state=DISABLED)

    def clearTextNetwork(self):
        self.textnetwork.config(state=NORMAL)
        self.textnetwork.delete('1.0', END)
        self.textnetwork.insert(INSERT, '')
        self.textnetwork.config(state=DISABLED)

    # ----------------
    # WRITE TEXT
    # ----------------
    def writeText1(self, msg):
        self.text1.config(state=NORMAL)
        self.text1.insert(INSERT, "%s\n" % (msg))
        self.text1.see('end')  # see the last line
        self.text1.config(state=DISABLED)

    def writeLog(self, msg):
        self.writeText1(self.getTime()+">>"+msg+"\n")

    def writeText2(self, msg):
        #self.text2.config(state=NORMAL)
        self.text2.insert(INSERT, "%s\n" % (msg))
        #self.text2.config(state=DISABLED)

    def writeText3(self, msg):
        self.text3.config(state=NORMAL)
        self.text3.insert(INSERT, "%s\n" % (msg))
        self.text3.see('end')  # see the last line
        self.text3.config(state=DISABLED)

    def writeText4(self, msg):
        self.text4.config(state=NORMAL)
        self.text4.insert(INSERT, "%s\n" % (msg))
        self.text4.see('end')  # see the last line
        self.text4.config(state=DISABLED)

    def writeTextNetwork(self, msg):
        self.textnetwork.config(state=NORMAL)
        self.textnetwork.insert(INSERT, "%s\n" % (msg))
        self.textnetwork.see('end')  # see the last line
        self.textnetwork.config(state=DISABLED)

    def write(self, msg, window):
        """
        Writes the msg in the window
        :param msg: text to be written
        :param window: window to be used
        """
        if window == Judas.CONTEXT:
            self.writeText2(msg)
        elif window == Judas.FILES:
            self.writeText4(msg)
        elif window == Judas.CONTEXT_NOTIFY:
            self.writeText3(msg)
        elif window == Judas.NETWORK:
            self.writeTextNetwork(msg)


    def writeError(self, msg, window):

        if window == Judas.CONTEXT:
            self.writeText3("ERROR>%s" % (msg))
        elif window == Judas.FILES:
            self.writeText4("ERROR>%s" % (msg))
        elif window == Judas.CONTEXT_NOTIFY:
            self.writeText3(msg)
        elif window == Judas.NETWORK:
            self.writeTextNetwork("ERROR>%s" % (msg))

    def writeWarning(self, msg, window):
        if window == Judas.CONTEXT:
            self.writeText3("Warning>%s" % (msg))
        elif window == Judas.FILES:
            self.writeText4("Warning>%s" % (msg))
        elif window == Judas.CONTEXT_NOTIFY:
            self.writeText3(msg)
        elif window == Judas.NETWORK:
            self.writeTextNetwork("Warning>%s" % (msg))

    def appendToText1(self, text, color='black'):
        self.text1.configure(state=NORMAL)
        self.text1.tag_configure("color", foreground=color)
        self.text1.insert(END, text , "color")
        self.text1.configure(state=DISABLED)

    def writeInColor(self, word, stringwithwords):
        start_index = stringwithwords.find(word)
        first = 0
        while (start_index != -1):
            end_index = start_index + len(word)

            self.appendToText1(stringwithwords[first:start_index])
            self.appendToText1(stringwithwords[start_index:end_index], color='red')

            # check if there are more appearances in the same string
            start_index = stringwithwords.find(word, start_index + 1)
            if (start_index == -1):
                self.appendToText1(stringwithwords[end_index:])#, color='black')  # end string
            else:
                first = end_index

    # ----------------
    # NETWORK
    # ----------------
    def initializeNetwork(self):
        self.macs_ip = None
        self.macs = None
        self.ips = None
        self.address_list = None

    def getMacs(self):
        if self.macs is not None:
            return self.macs
        if self.macs_ip is not None:
            self.macs = self.macs_ip.keys()
            return self.macs
        return None

    def getIPs(self):
        if self.ips is not None:
            return self.ips
        if self.macs_ip is None:
            self.loadNetwork()
        self.ips = list(x for l in self.macs_ip.values() for x in l)
        #self.ips = list(dict.fromkeys(self.ips))
        return self.ips


    def getMac_IP(self):
        return self.macs_ip


    def loadPcap(self, pathnetwork):
        #self.browse_button_file()

        pathresults = self.cfg.get('JUDAS', 'results_folder')
        self.macs_picture = pathresults + "/" + 'mac.png'
        self.ips_picture = pathresults + "/" + 'ip.png'
        if pathnetwork is not None:
            # load pcap file
            self.macs_ip = eatn.generaGraph(pathnetwork, self.macs_picture, self.ips_picture, pathresults)
            if self.macs_ip is not None:
                self.writeLog('Network loaded, elements: %d' % len(self.macs_ip))
                return True
                #self.showNetworkInfo()
            else:
                self.writeLog('Network not loaded')
        else:
            self.writeLog('Network not selected')
        return False


    def getPathsFiles(self, type):
        if type is not None and self.filePaths is not None:
            paths = self.filePaths.get(type)
            if paths is None: paths = []
            return paths
        else:
            return []


    def loadNetwork(self):
        # 1.- check if we have files to load:
        #pf = self.getPathsFiles('.pcap')
        pf = self.cfg.get('JUDAS', 'network_file') #one file for now

        if os.path.exists(pf):
            #load info from files:
            if self.loadPcap(pf) is None:
                self.writeError('.pcap files not loaded', Judas.NETWORK)
        else:
            self.writeError('.pcap files not loaded, please check path of .pcap files in judas.conf', Judas.NETWORK)


    def showNetworkInfo(self):
        # Initialise:
        self.loadNetwork()
        mac_ip = self.getMac_IP()

        if mac_ip is None:
            self.writeError('Please load a network (.pcap file) first', Judas.NETWORK)

        else:
            str =''
            for m in mac_ip:
                ip_list = mac_ip.get(m)
                str = "%sMAC: %s\n" % (str,m)
                for ip in ip_list:
                    str = "%s  ->IP:%s\n" % (str,ip)

            self.clearTextNetwork()
            self.writeTextNetwork(str)
            # show graphs for macs and ips:
            self.openImage(self.macs_picture, 'MAC addresses')
            self.openImage(self.ips_picture, 'IP addresses')
            self.writeLog('%s files processed and the result is shown in the main window.' % self.getPathsFiles('.pcap'))


    def searchInfoPublicIP(self):
        ips = self.getIPs()

        if ips is not None:
            self.address_list = eatn.getInfoIP(ips)

            if isinstance(self.address_list, list):
                str = ''
                for a in self.address_list:
                    str = "%s%s\n" % (str,a)

                self.clearText2()
                self.writeText2("\n --- ipapi output --- \n" + str)
                return True

            else:
                self.writeWarning('Unexpected result searching information about Public IPs, no results available', Judas.CONTEXT)
                self.writeWarning('Unexpected result searching information about Public IPs, no results available', Judas.FILES)

            apikeyVT = self.getAPIkeyVT()
            if apikeyVT is not None and len(apikeyVT)>0:
                str_resVT = eatn.getInfoIPVT(ips, apikeyVT)
                if len(str_resVT)>0:
                    self.writeText2("\n --- VirusTotal output --- \n" + str_resVT)

        else:
            self.writeWarning('Please show the network info first to read the .pcap file', Judas.CONTEXT)
            self.writeWarning('Please show the network info first to read the .pcap file', Judas.FILES)
        return False

    def searchUsersPublicInfo(self):
        """
        This method search for public info about the users
        :return: a string with the matches found (if any)
        """
        if self.context is None:
            self.writeError('Please, select folder with .json files first...', Judas.CONTEXT)
            return False

        # 0.- Check API key:
        apikeyPipl = self.getAPIkeyPipl()
        self.clearText2()
        if len(apikeyPipl)>0:
                self.writeText2("\n --- Pipl output --- \n" )

        else:
            self.writeError('No API Key found for users')
            return False

        # 1.- Get users
        users = self.context.getall(eatj.Context.USER)

        # 2.- Perform the requests:
        for u in users:
            email = u'%s' % u.getEmail()
            name = u'%s' % u.getName()
            lname = u'%s' % u.getFamilyName()
            # print(u)
            # print('Pipl (API Key:%s) Requested info for:%s, %s, %s' % (apikeyPipl[0], email, name, lname))
            request = pipl.SearchAPIRequest(email=email, first_name=name, last_name=lname, api_key=apikeyPipl[0])
            response = request.send()

            # 3.- Analyse the response:
            self.writeText2('--------- User (id:%s, name:%s)' % (u.getId(), u.getCompleteName()))
            if response.name is not None: self.writeText2('Name:%s' % response.name)
            if response.username is not None: self.writeText2('Username:%s' % response.username)
            if response.gender is not None: self.writeText2('Gender:%s' % response.gender)
            if response.phone is not None: self.writeText2('Phone:%s' % response.phone)
            if response.address is not None: self.writeText2('Address:%s' % response.address)
            if response.origin_country is not None: self.writeText2('Origin country:%s' % response.origin_country)
            if response.education is not None: self.writeText2('Education:%s' % response.education)
            if response.ethnicity is not None: self.writeText2('Ethnicity:%s' % response.ethnicity)
            if response.image is not None: self.writeText2('Image:%s' % response.image)
            if response.job is not None: self.writeText2('job:%s' % response.job)
            if response.language is not None: self.writeText2('Language:%s' % response.language)
            if response.matching_sources is not None: self.writeText2('Matching sources:%s' % response.matching_sources)

    def searchDevicePublicInfo(self):
        """
        This method search for public info about the devices
        :return: a string with the matches found (if any)
        """
        if self.context is None:
            self.writeError('Please, select folder with .json files first...', Judas.CONTEXT)
            return False

        # 0.- Check API key:
        if self.apiShodan is None:
            apikey = self.getAPIkeyShodan()
            self.clearText2()
            if len(apikey)>0:
                    self.writeText2("\n --- Shodan output --- \n" )

            else:
                self.writeError('No API Key found for devices')
                return False

            # 1.- Get api:
            self.apiShodan = shodan.Shodan(apikey)

        # 2.- Get devices
        devices = self.context.getall(eatj.Context.DEVICE)

        # 3.- Perform the requests:
        for d in devices:
            try:
                # Search Shodan
                results = self.apiShodan.search(d.getId())

                # Show the results
                self.write('Results found for Device(id:%s):' % d.getId(), Judas.CONTEXT)
                self.write('{}'.format(results['total']), Judas.CONTEXT)
                for result in results['matches']:
                    self.write('IP: {}'.format(result['ip_str']), Judas.CONTEXT)
                    self.write(result['data'], Judas.CONTEXT)
                    self.write('', Judas.CONTEXT)

            except shodan.APIError:
                self.writeError('Error while processing Shodan requests for device:%s' % d.getId(), Judas.CONTEXT)

        # Now, for addresses with IP (if any):
        addresses = self.context.getall(eatj.Context.ADDRESS)
        for a in addresses:
            try:
                if len(a.getBackpack(eatj.Address.IP))>0:
                    # Search Shodan
                    ip = a.getBackpack(eatj.Address.IP)[0]
                    results = self.apiShodan.search(ip)

                    # Show the results
                    self.write('Results found for Address (id:%s) with IP %s:' % (a.getId(), ip), Judas.CONTEXT)
                    self.write('{}'.format(results['total']), Judas.CONTEXT)
                    for result in results['matches']:
                        self.write('IP: {}'.format(result['ip_str']), Judas.CONTEXT)
                        self.write(result['data'], Judas.CONTEXT)
                        self.write('', Judas.CONTEXT)

            except shodan.APIError:
                self.writeError('Error while processing Shodan requests for address:%s' % a.getId(), Judas.CONTEXT)


    def correlate_network(self):
        "Correlate the results of the network (.pcap file) with the current context"
        str_out = ''

        if self.context is None:
            self.writeWarning('Please, select a context first...', Judas.NETWORK)
            return None
        if self.getMac_IP() is None:
            self.writeWarning('Please, select a network first...', Judas.NETWORK)
            return None

        if self.address_list is None:
            # search info first...
            self.writeLog('Searching information about public IPs...')
            self.searchInfoPublicIP()

        #in self.address_list is info about addresses that can be correlated with the data in the context
        str_out = self.context.correlateNetworkAddresses(self.address_list)

        if str_out is not None:
            self.clearTextNetwork()
            self.writeTextNetwork(str_out)
            self.writeLog('Correlation between the context and network items done...')
            self.writeTextNetwork('Correlation between the context and network items done...')
            self.write('Correlation between the context and network items done...', window=Judas.CONTEXT_NOTIFY)
        else:
            self.writeError('Correlation not possible...', Judas.NETWORK)

    def addNetworkToContext(self):
        if self.context is None:
            self.writeWarning('Please, select a context first...', Judas.CONTEXT)
            return None
        if self.getMac_IP() is None:
            self.writeWarning('Please, select a network first...', Judas.CONTEXT)
            return None
        if self.address_list is None:
            # search info first...
            self.searchInfoPublicIP()

        for a in self.address_list:
            self.context.addItem(a)

        self.context.cannibalism()

    #----------------
    # WORKING WITH THE CONTEXT
    #----------------
    def destroyContext(self):
        if self.context is not None:
            self.context.__del__()
        self.clearText1()
        self.clearText2()
        self.clearText3()
        self.initVariables()

    def showContent(self):
        self.outputfile = 'jsoncontent.txt'

        path = self.getPath()

        if os.path.isdir(path): #is a directory
            eat.writeJsonDirectory(path, self.outputfile)

        else:
            eat.writeJson(path, self.outputfile, 'w')

        # write content of the output file in the GUI
        self.clearText4()
        f = open(self.outputfile, "r")
        self.writeText4(f.read())
        f.close()

    def showContextGraph(self):
        "Shows graphically the context"
        if self.context is None:
            self.writeError('Please, select folder with .json files first...', Judas.CONTEXT)
            return False

        fileimg = 'context'
        value_mode = self.comboGraph.get()
        if value_mode == self.GRAPH_MODE0: mode = 0
        elif value_mode == self.GRAPH_MODE1: mode = 1
        elif value_mode == self.GRAPH_MODE2: mode = 2
        if mode!=1: #Image is needed:
            res = self.context.showContext(output=fileimg, mode=mode)
            msg = 'Summary graph (only users and devices) generated for %s' % res
            if bool(res):
                self.openImage('results/'+fileimg + '.gif')

        if mode>0: #Web is needed:
            if self.http_handler is not None:
                self.http_handler.stop() # stop the handler

            self.http_handler = self.context.showContext(output=None, objectsofinterest=None, mode=mode)
            res = self.http_handler
            msg = 'Interactive graph in http://localhost:8000/force/judas.html'

        if bool(res):
            self.write(msg, Judas.CONTEXT_NOTIFY)
            self.writeLog(msg)
            return True

        else:
            self.writeError('No graph available', Judas.CONTEXT)
            return False

    def getRelevantExtensions(self):
        ret = []
        if self.varJson.get(): ret.append('.json')
        if self.varPcap.get(): ret.append('.pcap')

        return ret


    def getRelevantFiles(self, addto=True):
        """
        This method process all the files of interest in a folder and sub-folders
        :param addto: Add files to the current structure avoiding duplicates
        :return: prints the list of files considered, and updates the variable with the list of relevant files
        """
        self.myFiles = {}
        path = self.getPath()
        relevant = self.getRelevantExtensions()
        candidate = eatj.Context.getFiles(path, {}, relevant, False)
        if not addto or (self.filePaths is None or len(self.filePaths)==0):
            self.filePaths = candidate
        else:
            # mix:
            kc = candidate.keys()
            for k in kc:
                vals = self.filePaths.get(k)
                if vals is None: vals=[]
                vals2 = candidate.get(k)
                if vals2 is None: vals2=[]
                vals = list(set(vals + vals2))
                self.filePaths.update({k:vals})

        if len(self.filePaths)>0:
            self.clearText2()
            string = ''
            for k in self.filePaths:
                vals = self.filePaths.get(k)
                vals_str = ["file(name):%s, filepath:%s\n" % (ntpath.basename(filepath) , filepath)
                              for filepath in vals]
                vals_str = ''.join(vals_str)
                string = "%s%s" % (string, vals_str)
            self.writeText2(string)
            self.writeLog('Extracted relevant files from folder: %s\n%s' % (path, string))

        return True


    def showContext(self):
        "Only shows the context"

        if self.context is None:
            self.writeWarning('Searching .json files in the default folder...', Judas.CONTEXT)
            self.extractContext()

        #print the context again:
        saved = self.context.save_context(eatj.Context.getdefaultfile())
        if saved:
            self.clearText2()
            f = open(eatj.Context.getdefaultfile(), "r")
            self.writeText2(f.read())
            f.close()
            return True
        else:
            self.writeError('Error printing the context', Judas.CONTEXT)

    def extractContext(self, showLogs=True):
        if self.context is None:
            self.context = eatj.Context(self.cfg.get("JUDAS", "context_folder"))

        if self.filePaths is None or len(self.filePaths)==0:
            self.getRelevantFiles()

        # Get JSONs (if any):
        if self.filePaths.get('.json'):
            jsonfiles = self.filePaths.get('.json')
            #store files to be shown
            self.files_processed = self.context.createContextFromJson(jsonfiles)

            if not bool(self.files_processed):
                self.writeError('Context not extracted...', Judas.FILES)
                self.context = None
                return False
            else:
                #if showLogs:
                not_processed = [x for x in jsonfiles if x not in self.files_processed]
                self.writeLog('\n----------Context extracted from files (%d):\n %s' % (len(self.files_processed), ''.join(["%s\n" % j for j in self.files_processed])))
                self.writeLog('\n---------Not processed (%d): \n%s' % (len(not_processed), ''.join(["%s\n" % j for j in not_processed])))

            return self.showContext()
        else:
            self.writeError('Context not extracted because problems with the path ... check directory path for .json files', Judas.FILES)
            self.context = None
            return None

    def selectandloadcontext(self):
        # Destroy current context:
        self.destroyContext()
        # Select folder:
        self.browse_button()
        # Extract context:
        res = self.extractContext()
        if res:
            self.writeLog('Context extracted from directory:%s' % self.getPath())
        else:
            self.writeLog('(something happened) Context not extracted from directory:%s' % self.getPath())


    def searchKeywords(self):
        "Search keywords into the Context"
        words = self.entryKeyword.get().split(",")

        if len(words)>0 and self.context is not None:
            # string with the words
            res = self.context.searchKeywords(words, True)

            if res is not None:
                self.clearText2()
                self.writeText2('Results after search keywords: %s in the current context:'% words)
                self.writeText2(str(res))

            else:
                self.writeLog('No keywords (%s) in the current context' % words)
        else:
            self.writeError('Please, provide a list of keywords separate by comma (,)', Judas.CONTEXT)



    def searchKeywordsFile(self):
        "Search keywords into json Files"
        words = self.entryKeywordFile.get().split(",")

        if len(words)>0:
            # string with the words
            res = eat.searchInDirJson(words, self.label_text.get())

            if res is not None:
                files = res.get('files')
                descr = res.get('summary')

                if files is not None and len(files)>0:
                    self.writeLog('List of files with keywords:%s\n%s' % (words, files))
                    self.clearText4()
                    self.writeText4(descr)

                else:
                    self.writeLog('No keywords (%s) in files' % words)
            else:
                self.writeLog('No keywords (%s) in files' % words)
        else:
            self.writeError('Please, provide a list of keywords separate by comma (,)', Judas.FILES)

    def generateOptions(self):
        """
        :return: a list with options to show in a
        """

    def getBase64(self):
        if self.context is not None:
            b64 = self.context.getBase64()
            if len(b64)>0:
                self.writeText2(self.context.getBase64())
                self.writeLog('Search base64 strings -- produces results')
            else:
                self.writeLog('Search base64 strings -- does not produce results')
                self.writeWarning('Search base64 strings -- does not produce results', Judas.CONTEXT)
        else:
            self.writeError('Please, select a context first...', Judas.CONTEXT)


    @staticmethod
    def plotGraphX(rects, label_rects, x_label, y_label, title, bar_groups):
        """
        Adapted from: https://pythonspot.com/matplotlib-bar-chart/ and
        http://sparkandshine.net/en/draw-with-matplotlib-stacked-bar-charts-with-error-bar/
        This method plots a graph, bar-chart, two columns each group
        :param rects: set of values for the bars
        :param label_rects: labels for the legends (all bars)
        :param x_label: label for the x-axes in the graph
        :param y_label: label for the y-axes in the graph
        :param title: title for the plot
        :param bar_groups: name of the groups
        :return: this method prints a graph with the values given as parameters
        """
        """
        fig, ax = plt.subplots()
        n_groups = len(bar_groups)
        index = np.arange(n_groups)
        bar_width = 0.20 #35
        opacity = 0.8
        colors = ['navy', 'green', 'darkorange', 'purple', 'red', 'olive', 'tomato']

        i=0
        for rect_tup in rects:
            rect = plt.bar(index + bar_width*i, rect_tup, bar_width,
                         alpha=opacity,
                         color=colors[i%len(colors)],
                         label=label_rects[i])
            eatj.Anything.autolabel(rect, ax)
            i += 1

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(index+bar_width, bar_groups)
        plt.legend()

        plt.tight_layout()
        plt.show()
        """

    def summary(self):
        """
        Plots a summary of the context
        """
        if self.context is None:
            self.writeError('Please, select a context first...', Judas.CONTEXT)
        else:
            # 1.- Get summary of Anything:
            anything_statistics = eatj.Anything.printStatistics(False, False)
            class_name = anything_statistics.get('order')
            total_inst_class = anything_statistics.get('total')
            unique_obj_class = anything_statistics.get('unique')
            any_statistics = anything_statistics.get('summary')
            # 2.- Get summary of the context:
            context_summary = self.context.getSummary()

            # Process to complete the info, following the order in class_name:
            number_rel = ()
            number_fil = ()
            for k in class_name:
                dicto = context_summary.get(k)
                number_rel = number_rel + (dicto.get('relationships'),)
                number_fil = number_fil + (dicto.get('files'),)

            self.clearText2()
            self.writeText2(context_summary.get('summary'))
            self.writeText2(any_statistics)

            # 3.- Plot results:
            rects = [total_inst_class, unique_obj_class, number_rel, number_fil]
            label_rects = ['# Instances Created (total)', '# Instances with unique value (used)', '# Relationships',
                           '# Source files']
            self.plotGraphX(rects, label_rects, 'Class', 'Number of items', 'Summary of values', class_name)


    def showidcontext(self):
        if self.context is None:
            self.writeError('Please, select a context first...', Judas.CONTEXT)

        else:
            ids = self.context.getlistID()

            if len(ids)>0:
                self.clearText2()
                self.writeText2(ids)
            else:
                self.writeLog('Warning!! No IDs detected for the context.')


def main():
    Judas().mainloop()


if __name__ == "__main__":
    main()



