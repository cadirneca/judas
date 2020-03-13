# -------
# judas. JSON Users and Devices AnalySys tool
# -------
# @author:      Ana Nieto,
# @email:       nieto@lcc.uma.es
# @institution: University of Malaga
# @country:     Spain
# @website:     https://www.linkedin.com/in/ana-nieto-72b17718/
######

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import *
from tkinter.ttk import Combobox

from eatingJson import *
from PIL import Image
import datetime
import eating as eat
import eatingNetwork as eatn
import ntpath
import shodan


class Judas(Frame):

    FILES = 'FILES'
    CONTEXT = 'CONTEXT'
    API = 'API'
    REPORT = 'REPORT'
    GRAPH_MODE0 = ".gif(Summary)"
    GRAPH_MODE1 = "Web(All)"
    GRAPH_MODE2 = "Both"

    def __init__(self):
        # Init variables:
        self.initVariables()

        # Init frame:
        Frame.__init__(self)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.master.title("JSON Users and Devices AnalysiS tool")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        img = tk.Image("photo", file="judas.gif")
        self.master.tk.call('wm', 'iconphoto', self.master._w, img)

        #self.master.geometry("815x700")
        #icon_path = os.getcwd() + '/judas.ico'
        #self.master.wm_iconphoto(True, PhotoImage(file=icon_path))
        self.grid(sticky=W + E + N + S)

        # Notebook
        self.notebook = ttk.Notebook(self.master)
        self.frameFiles = Frame(self.notebook)      # frame to handle files
        self.frameFiles.grid(sticky=W + E + N + S)
        self.frameContext = Frame(self.notebook)    # frame to handle the context
        self.frameContext.grid(sticky=W + E + N + S)
        self.frameAPIs = Frame(self.notebook)    # frame to handle the context
        self.frameAPIs.grid(sticky=W + E + N + S)
        self.frameReport = Frame(self.notebook)    # frame to handle the context
        self.frameReport.grid(sticky=W + E + N + S)

        # Initialize Tab for Files:
        self.setup_frame_for_files() # Initialize self.frameFiles

        # Initialize Tab for Context:
        self.setup_frame_for_context() # Initialize self.frameContext

        # Initialize Tab for API Keys:
        self.setup_frame_for_APIKeys() # Initialize self.frameAPIs

        # Initialize Tab for Report:
        self.setup_frame_for_Report()  # Initialize self.frameAPIs

        # Rest of configurations:
        self.notebook.add(self.frameContext, text="Context")
        self.notebook.add(self.frameFiles, text="Files")
        self.notebook.add(self.frameAPIs, text="API Keys")
        self.notebook.add(self.frameReport, text="Report")

        self.notebook.pack()
        self.pack()

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


    def setup_frame_for_files(self):

        self.frame_options = Frame(self.frameFiles)
        self.frame_options.grid(sticky=N+S+E+W)

        # -------- LOAD FILES
        self.button1 = Button(self.frame_options, text="Select default folder", command=self.selectandloadcontext)
        self.button1.grid(row=0, column=0, sticky=N+S+E+W)
        self.initLabelText()
        self.label = Label(self.frame_options, textvariable=self.label_text, wraplength=700, justify=LEFT, anchor=W)
        self.label.grid(row=0, column=1, sticky=N + S + E + W)

        # Panel to select type of files
        self.frameFileType = Frame(self.frame_options)
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



        # BOTTOM
        self.panedBottomFile = PanedWindow(self.frameFiles, orient=HORIZONTAL)

        self.labelKeyFile = Label(self.panedBottomFile, text="Keywords:")
        self.entryKeywordFile = Entry(self.panedBottomFile, width=50)
        self.entryKeywordFile.insert(INSERT, " ")
        self.button5 = Button(self.panedBottomFile, text="Search", command=self.searchKeywordsFile)

        self.panedBottomFile.grid(row=2, sticky=W + E + N + S)

        self.panedBottomFile.add(self.labelKeyFile)
        self.panedBottomFile.add(self.entryKeywordFile)
        self.panedBottomFile.add(self.button5)

        # -------- NETWORK FILES
        # Label for results:
        self.label_text7 = StringVar()
        self.label_text7.set('Results:')
        self.label7 = Label(self.frameFiles, textvariable=self.label_text7, justify=CENTER, anchor=W)
        self.label7.grid(row=3, sticky=W + E)

        # - Results, errors and warnings...
        self.panedBottomFileErrors = PanedWindow(self.frameFiles, orient=VERTICAL)

        self.text4 = Text(self.panedBottomFileErrors, background='snow')  # , wrap = NONE)
        self.text4.insert(INSERT, '\n')  # lorem.paragraph())
        self.text4.config(state=DISABLED)  # only for read

        self.scrollbar4 = Scrollbar(self.panedBottomFileErrors, orient=VERTICAL, command=self.text4.yview)
        self.text4['yscroll'] = self.scrollbar4.set

        self.scrollbar4.pack(side="right", fill="y")
        self.text4.pack(side="left", fill="both", expand=True)

        self.panedBottomFileErrors.grid(row=4, sticky=W + E + N + S)

        self.frameFiles.pack()

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
        self.button14 = Button(self.panedResults, text="Save Results", bg='blue', command=self.save_results)

        self.panedResults.add(self.button14)
        self.panedResults.add(self.label5)
        self.panedResults.add(self.text2)

        self.panedResults.grid(row=0, column=0, columnspan=2, sticky=W + E + N + S)


        # RIGHT:
        self.panedButtons = PanedWindow(self.frameContext, orient=VERTICAL)  # , background='sky blue')

        self.button3 = Button(self.panedButtons, text="Show judas context", bg='deep sky blue',command=self.showContext)

        #graphs:
        self.pannedGraph = PanedWindow(self.panedButtons, orient=HORIZONTAL)
        self.comboGraph = Combobox(self.pannedGraph, state="readonly", values=(self.GRAPH_MODE0, self.GRAPH_MODE1,
                                                                               self.GRAPH_MODE2))
        self.comboGraph.set(self.GRAPH_MODE2)
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
        self.label_text3 = StringVar()
        self.label_text3.set('Network:')
        self.label3 = Label(self.panedButtons, textvariable=self.label_text3, justify=CENTER, anchor=W)
        self.button12 = Button(self.panedButtons, text="Show network info", bg='yellow', command=self.showNetworkInfo)
        self.button13 = Button(self.panedButtons, text="Acquire Public IP info", bg='yellow',command=self.searchInfoPublicIP)
        self.button15 = Button(self.panedButtons, text="Correlate with context", bg='blue',command=self.correlate_network)
        self.button16 = Button(self.panedButtons, text="Add to context", bg='blue',
                               command=self.addNetworkToContext)
        self.label_text8 = StringVar()
        self.label_text8.set('Users:')
        self.label8 = Label(self.panedButtons, textvariable=self.label_text8, justify=CENTER, anchor=W)
        self.button17 = Button(self.panedButtons, text="Acquire Public User Info", bg='yellow',command=self.searchUsersPublicInfo)

        self.label_text9 = StringVar()
        self.label_text9.set('Devices:')
        self.label9 = Label(self.panedButtons, textvariable=self.label_text9, justify=CENTER, anchor=W)
        self.button18 = Button(self.panedButtons, text="Acquire Public Device Info", bg='yellow',command=self.searchDevicePublicInfo)

        # self.panedButtons.add(self.button4)
        self.panedButtons.add(self.button3)
        self.panedButtons.add(self.pannedGraph)
        self.panedButtons.add(self.label2)
        self.panedButtons.add(self.button6)
        self.panedButtons.add(self.button10)
        self.panedButtons.add(self.label3)
        self.panedButtons.add(self.button12)
        self.panedButtons.add(self.button13)
        self.panedButtons.add(self.button15)
        self.panedButtons.add(self.button16)
        self.panedButtons.add(self.label8)
        self.panedButtons.add(self.button17)
        self.panedButtons.add(self.label9)
        self.panedButtons.add(self.button18)
        self.panedButtons.grid(row=0, column=2, sticky=W + E + N + S)

        # BOTTOM
        self.panedBottom = PanedWindow(self.frameContext, orient=HORIZONTAL)

        self.labelKey = Label(self.panedBottom, text="Keywords:")
        self.entryKeyword = Entry(self.panedBottom, width=50)
        self.entryKeyword.insert(INSERT, "AB72C64C86AW2")
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
        self.text3['yscroll'] = self.scrollbar3.set

        self.scrollbar3.pack(side="right", fill="y", expand=False)
        self.text3.pack(side="left", fill="both", expand=True)

        self.panedEWContext.grid(row=3, columnspan=3, sticky=W + E + N + S)

        self.frameContext.pack()



    def setup_frame_for_APIKeys(self):

        self.frameAPIs.grid(sticky=N + S + E + W)

        # 0 - Buttons for load/save API keys
        self.button19 = Button(self.frameAPIs, text="Load API Keys", command=self.loadAPIkeys)
        self.button19.grid(column=0, row=0, sticky=E + W)
        self.button20 = Button(self.frameAPIs, text="Save API Keys", command=self.saveAPIkeys)
        self.button20.grid(column=1, row=0, sticky=E + W)

        # 1 - Network info
        self.labelNetworkInfo = Label(self.frameAPIs, text="NETWORK")
        self.labelNetworkInfo.grid(column=0, row=1, columnspan=2,  sticky=E + W)

        # VirusTotal
        self.labelVT = Label(self.frameAPIs, text="VirusTotal API Key:")
        self.labelVT.grid(column=0, row=2)
        self.entryVT = Entry(self.frameAPIs, width=60)
        self.entryVT.grid(column=1, row=2, sticky=E + W) #, columnspan=3

        # PassiveTotal
        self.labelPT = Label(self.frameAPIs, text="Passive Total API Key:")
        self.labelPT.grid(column=0, row=3)
        self.entryPT = Entry(self.frameAPIs, width=60)
        self.entryPT.grid(column=1, row=3, sticky=E + W)

        # 2 - Devices
        self.labelNetworkInfo = Label(self.frameAPIs, text="DEVICES")
        self.labelNetworkInfo.grid(column=0, row=4, columnspan=2,  sticky=E + W)

        # Shodan
        self.labelShodan = Label(self.frameAPIs, text="Shodan API Key:")
        self.labelShodan.grid(column=0, row=5)
        self.entryShodan = Entry(self.frameAPIs, width=60)
        self.entryShodan.grid(column=1, row=5,  sticky=E + W)

        # 3 - Users
        self.labelNetworkInfo = Label(self.frameAPIs, text="USERS")
        self.labelNetworkInfo.grid(column=0, row=6, columnspan=2,  sticky=E + W)
        # Pipl
        # - Business
        self.labelPiplBus = Label(self.frameAPIs, text="Pipl API Key Business:")
        self.labelPiplBus.grid(column=0, row=7)
        self.entryPiplBus = Entry(self.frameAPIs, width=60)
        self.entryPiplBus.grid(column=1, row=7, sticky=E + W)
        # - Social
        self.labelPiplSoc = Label(self.frameAPIs, text="Pipl API Key Social:")
        self.labelPiplSoc.grid(column=0, row=8)
        self.entryPiplSoc = Entry(self.frameAPIs, width=60)
        self.entryPiplSoc.grid(column=1, row=8, sticky=E + W)
        # - Contact
        self.labelPiplCon = Label(self.frameAPIs, text="Pipl API Key Contact:")
        self.labelPiplCon.grid(column=0, row=9)
        self.entryPiplCon = Entry(self.frameAPIs, width=60)
        self.entryPiplCon.grid(column=1, row=9, sticky=E + W)

        self.frameAPIs.pack()

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


        self.frameReport.pack()

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
        filename = filedialog.askdirectory() 

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

    def save_file_as(self, text, defextension='.txt'):
        self.filename = filedialog.asksaveasfilename(defaultextension=defextension) 

        if self.filename is not None and len(self.filename)>0:
            f = open(self.filename, 'w')
            f.write(text)
            f.close()
            messagebox.showinfo('JSON Users and Devices AnalysyS tool', 'File Saved')

    def save_logs(self):
        self.save_file_as(self.getLogs())

    def save_results(self):
        self.save_file_as(self.getResults())

    def openImage(self, filename, title="judas context graph"):
        img = Image.open(filename)
        img.show()


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


    def loadAPIkeys(self):
        """ Loads a file with API keys inside"""
        # open file
        filename = filedialog.askopenfilename(initialdir="/", title="Select file with API Keys",
                                filetypes=(("JSON file", "*.json"), ("all files", "*.*")))        
        if not bool(filename):
            return None

        # get dictionary:
        try:
            with open(filename, 'r') as fp:
                dicto = json.load(fp)

            if dicto is None:
                return False
        except:
            return False

        # update data
        self.entryVT.insert(INSERT, str(dicto.get("VirusTotal")))
        self.entryPT.insert(INSERT, str(dicto.get("PassiveTotal")))
        self.entryShodan.insert(INSERT, str(dicto.get("shodan")))
        self.entryPiplBus.insert(INSERT, str(dicto.get("piplbus")))
        self.entryPiplSoc.insert(INSERT, str(dicto.get("piplsoc")))
        self.entryPiplCon.insert(INSERT, str(dicto.get("piplcon")))

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
        else:
            self.writeLog('Warning!! Default context not loaded...')

        # Initialise Network Parameters
        self.initializeNetwork()



    def initLabelText(self):
        self.label_text = StringVar()
        self.label_text.set('sources')
        self.is_directory = True


    def setLabel4(self, path):
        self.label_text4.set(path)

    def initLabelText4(self):
        self.label_text4 = StringVar()
        self.setLabel4('sources/network/dfrws_police.pcap')

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


    def writeError(self, msg, window):

        if window == Judas.CONTEXT:
            self.writeText3("ERROR>%s" % (msg))
        elif window == Judas.FILES:
            self.writeText4("ERROR>%s" % (msg))

    def writeWarning(self, msg, window):
        if window == Judas.CONTEXT:
            self.writeText3("Warning>%s" % (msg))
        elif window == Judas.FILES:
            self.writeText4("Warning>%s" % (msg))

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
                self.appendToText1(stringwithwords[end_index:])
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
        if self.macs_ip is not None:
            self.ips = list(x for l in self.macs_ip.values() for x in l)
            return self.ips
        return None

    def getMac_IP(self):
        return self.macs_ip


    def loadPcap(self, path):
        #self.browse_button_file()

        self.macs_picture = 'results/mac.png'
        self.ips_picture = 'results/ip.png'
        if path is not None:
            # load pcap file
            self.macs_ip = eatn.generaGraph(path, self.macs_picture, self.ips_picture)
            if self.macs_ip is not None:
                self.writeLog('Network loaded')
                #self.showNetworkInfo()
        else:
            self.writeLog('Network not selected')


    def getPathsFiles(self, type):
        if type is not None and self.filePaths is not None:
            paths = self.filePaths.get(type)
            if paths is None: paths = []
            return paths
        else:
            return []


    def loadNetwork(self):
        # 1.- check if we have files to load:
        pf = self.getPathsFiles('.pcap')

        if len(pf)>0:
            #load info from files:
            self.loadPcap(pf[0]) #one file for now
        else:
            self.writeError('.pcap files not loaded, please check the presence of .pcap files in the default folder', Judas.FILES)


    def showNetworkInfo(self):
        # Initialise:
        self.loadNetwork()
        mac_ip = self.getMac_IP()

        if mac_ip is None:
            self.writeError('Please load a network (.pcap file) first', Judas.CONTEXT)

        else:
            str =''
            for m in mac_ip:
                ip_list = mac_ip.get(m)
                str = "%sMAC: %s\n" % (str,m)
                for ip in ip_list:
                    str = "%s  ->IP:%s\n" % (str,ip)

            self.clearText2()
            self.writeText2(str)
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
        users = self.context.getall(Context.USER)

        # 2.- Perform the requests:
        for u in users:
            email = u'%s' % u.getEmail()
            name = u'%s' % u.getName()
            lname = u'%s' % u.getFamilyName()
            # print(u)
            # print('Pipl (API Key:%s) Requested info for:%s, %s, %s' % (apikeyPipl[0], email, name, lname))
            request = SearchAPIRequest(email=email, first_name=name, last_name=lname, api_key=apikeyPipl[0])
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
        devices = self.context.getall(Context.DEVICE)

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
        addresses = self.context.getall(Context.ADDRESS)
        for a in addresses:
            try:
                if len(a.getBackpack(Address.IP))>0:
                    # Search Shodan
                    ip = a.getBackpack(Address.IP)[0]
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
            self.writeWarning('Please, select a context first...', Judas.CONTEXT)
            return None
        if self.getMac_IP() is None:
            self.writeWarning('Please, select a network first...', Judas.CONTEXT)
            return None

        if self.address_list is None:
            # search info first...
            self.writeLog('Searching information about public IPs...')
            self.searchInfoPublicIP()

        #in self.address_list is info about addresses that can be correlated with the data in the context
        str_out = self.context.correlateNetworkAddresses(self.address_list)

        if str_out is not None:
            self.clearText2()
            self.writeText2(str_out)
            self.writeLog('Correlation between the context and network items done...')
            self.writeText3('Correlation between the context and network items done...')
        else:
            self.writeError('Correlation not possible...', Judas.CONTEXT)

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
            msg = 'Interactive graph in http://localhost:8000/force/force2.html'

        if bool(res):
            self.write(msg, Judas.CONTEXT)
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
        candidate = Context.getFiles(path, {}, relevant, False)
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
        saved = self.context.save_context(Context.SAVE_CONTEXT)
        if saved:
            self.clearText2()
            f = open(Context.SAVE_CONTEXT, "r")
            self.writeText2(f.read())
            f.close()
            return True
        else:
            self.writeError('Error printing the context', Judas.CONTEXT)

    def extractContext(self, showLogs=True):
        if self.context is None:
            self.context = Context()

        if self.filePaths is None or len(self.filePaths)==0:
            self.getRelevantFiles()

        # Get JSONs (if any):
        if self.filePaths.get('.json'):
            jsonfiles = self.filePaths.get('.json')
            files_processed = self.context.createContextFromJson(jsonfiles)

            if not bool(files_processed):
                self.writeError('Context not extracted...', Judas.FILES)
                self.context = None
                return False
            else:
                #if showLogs:
                not_processed = [x for x in jsonfiles if x not in files_processed]
                self.writeLog('\n----------Context extracted from files (%d):\n %s' % (len(files_processed), ''.join(["%s\n" % j for j in files_processed])))
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
            Anything.autolabel(rect, ax)
            i += 1

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(index+bar_width, bar_groups)
        plt.legend()

        plt.tight_layout()
        plt.show()

    def summary(self):
        """
        Plots a summary of the context
        """
        if self.context is None:
            self.writeError('Please, select a context first...', Judas.CONTEXT)
        else:
            # 1.- Get summary of Anything:
            anything_statistics = Anything.printStatistics(False, False)
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



