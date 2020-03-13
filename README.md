
JSON USERS AND DEVICES ANALYSIS (JUDAS) TOOL

#---------------------------------------------
# Intro
#---------------------------------------------

JUDAS is a proof of concept of the latest work I am doing, oriented to the IoT-Forensics research line.

Please, do not hesitate to improve this code and adapt it to your own needs ... also, I am not an expert in software
development, so I hope that those more used to work with python make their improvements and forgive my mistakes. I'm
just learning this language.

If you find this application or my work interesting, please do not forget to reference it.

Thank you very much for your interest and enjoy!!!

#---------------------------------------------
# JUDAS objective
#---------------------------------------------

JUDAS creates an interpretation of the context of a digital investigation, starting by processing the JSON files.
JUDAS will extract the devices and users but following a set of criteria defined during the parsing of these files.
This uses hooks to read from JSONs and create the objects of the context. At the end only objects with different
identifiers survives and form part of the context. The taccustomedool recognise equal items and combines all the information in
a single object. Also, some checks with open source intelligence (OSINT) services are developed.

Further details will be published (I hope) soon.

#---------------------------------------------
# How to use JUDAS
#---------------------------------------------

Call the file judas.py to use the GUI. This GUI calls to methods implemented in the files eatingJson and eatingNetwork.
The file 'eating' contains some methods that can be used to make basic operations with JSONs (e.g., printing).

By default JUDAS eats all the files of interest in a digital investigation case folder. The folder 'sources' contains
a set of files that can be used for testing. However, you can select another folder using the tab 'Files' in the GUI.

- Go to 'Files' to control the default folder for the digital investigation. By default it use 'sources'.
- Results (graphs, .dot, etc.) are stored in the folder 'results'

The tool will then analyse the folder recursively to classify the files based on their type. It will start the analysis
with JSON files.

In the GUI:
- 'Show JUDAS context' shows all the objects created to represent the context.
- 'Plot' shows graphically the context. '.gif' only for users and devices, 'Web' to visualise all the objects and the
   relationships in the browser.
- 'Show IDs' shows only the identifiers for the objects in the context.
- 'Show network info' shows the data extracted from the .pcap (if any)
- 'Acquire public IP info' checks public information for public IPs identified in the .pcap.
- 'Correlate with context' shows some correlations with the objects in the context (Addresses)
- 'Add to context' adds the new info collected (new Addresses) to the context.
- 'Acquire Public User Info' checks public information about users in the context.
- 'Acquire Public Device Info' checks public information about devices in the context.

Check the tab 'API Keys' in order to see the external services that may require API Keys (e.g. Shodan, VirusTotal).
PassiveTotal is included but finally is not used in practice (yet).

The tab 'Report' prints the results of some operations to simplify the traceability of the operations made with the
tool and then help in the reporting.


#---------------------------------------------
# Contact
#---------------------------------------------

Please, any request/comment to my address: nieto@lcc.uma.es
This is my public profile: https://www.nics.uma.es/nieto
Thank you for your interest.
