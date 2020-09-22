######
# @author:      Ana Nieto
# @country:     Spain
# @website:     https://www.linkedin.com/in/ananietojimenez/
######

import subprocess
import json
import pprint
import warnings
import os
import sys
from auxiliar import auxiliar as aux
import tempfile
import shutil

#-----------------------------------------
#       AUXILIAR METHODS
#-----------------------------------------
def getSample():
    result = subprocess.run(['ls', '-l'], capture_output=True)
    #salida tal cual:
    print(result.stdout)
    #salida bonita:
    print(result.stdout.decode('utf-8'))

def parseOutputRowColumns(res):
    outputs = res.get("rows")
    meaning = res.get("columns")

    resParsed = []
    for o in outputs:
        out_dic = {}
        m = 0
        for v in o:
            out_dic.update({meaning[m]: v})
            m += 1
        resParsed += [out_dic]

    return resParsed

#-----------------------------------------
#       CALLING VOLATILITY METHODS
#-----------------------------------------
def getProfile(memoryPath, showOutput=False):
    """
    Returns the profile identified by volatility
    :param memoryPath: path to the file
    :param showOutput: if True the result of the command is printed. This param takes value False by default.
    :return: profile (string) identified by volatility.
    """
    try:
        # Get profile as json:
        res = subprocess.run(['vol.py', '-f', memoryPath, 'imageinfo', '--output', 'json'], capture_output=True)

        # Convert to json:
        res = json.loads(res.stdout.decode('utf-8'))

        # Show output (if required)
        if showOutput: pprint.pprint(res)

        # Get the preferred profile (instantiated)
        if res:# we have a profile!!
            mainProf = res.get("rows")[0][0].split(',')[0]

        # Return profile
        return mainProf

    except:
        print('getProfile>> Exception occurs')
        return ''


def runVol(memoryPath, command, profile=None, showOutput=False, showOriginal=False, checkProfile=True, added=''):
    """
    :param memoryPath: path to the file.
    :param command: runs a volatility command.
    :param profile: memory profile (try getProfile first).
    :param showOutput: if True the result of the command is printed. This param takes value False by default.
    :param showOriginal: showOriginal shows the original output returned by volatility.
    :return: requested values parsed
    """
    if profile is None and checkProfile:
        profile = getProfile(memoryPath)

        if len(profile)==0:
            msg = "runVol>> Please provide a valid memory profile"
            warnings.warn(msg)
            return []
    try:
        # Run command and get the result as json:
        if profile:
            res = subprocess.run(['vol.py', '-f', memoryPath, command, '--profile', profile, '--output', 'json', added], capture_output=True)
            if showOriginal:
                r2 = subprocess.run(['vol.py', '-f', memoryPath, command, '--profile', profile, added], capture_output=True)
                if r2 is not None: print(r2.stdout.decode('utf-8'))
        else:
            res = subprocess.run(['vol.py', '-f', memoryPath, command, '--output', 'json', added], capture_output=True)
            if showOriginal:
                r2 = subprocess.run(['vol.py', '-f', memoryPath, command, added], capture_output=True)
                if r2 is not None: print(r2.stdout.decode('utf-8'))

        # Convert to json:
        res = json.loads(res.stdout.decode('utf-8'))

        if res is None or len(res)==0: return []

        # Show output (if required)
        if showOutput: pprint.pprint(res)

        # Get values parsed
        output_parsed = parseOutputRowColumns(res)

        # Return structure of processes
        return output_parsed

    except:
        return []


def runVolshell(memoryPath, command, profile=None, added=''):
    """
    :param memoryPath: path to the file.
    :param command: runs a volatility command.
    :param profile: memory profile (try getProfile first).
    :return: requested values parsed
    """
    if profile is None:
        profile = getProfile(memoryPath)

        if len(profile)==0:
            msg = "runVolshell>> Please provide a valid memory profile"
            warnings.warn(msg)
            return []
    try:
        # Run command:
        res = subprocess.run(['vol.py', '-f', memoryPath, command, '--profile', profile, '--output', 'json', added], capture_output=True)

    except:
        return []

#-----------------------------------------
#       INTERFACE METHODS
#-----------------------------------------
def getProcesses(memoryPath, profile=None, listPID=False):
    """
    :param memoryPath: path to the file
    :param profile: memory profile (try getProfile first)
    :param listPID: if True only the list of PIDs is returned.
    :return: list of processes listed (pslist)
    """
    res = runVol(memoryPath, 'pslist', profile=profile, showOutput=False)

    if listPID: res = [x.get("PID") for x in res]

    return res

def getVADs(memoryPath, profile=None, listPID=False):
    """
    :param memoryPath: path to the file
    :param profile: memory profile (try getprofile first)
    :param listPID: if True only the graph for a set of process is generated
    :return: graph for the processes
    """
    if not listPID: listPID = getProcesses(memoryPath, profile=profile)
    pids = ','.join(listPID);

    for p in pids:
        vad = runVol(memoryPath, 'vadinfo', profile=profile, showOutput=False)



#-----------------------------------------
#       MEMORY ANALYSIS
#-----------------------------------------
def getHiddenProcesses(memoryPath, profile=None, checkProfile=False, showOutput=False, showOriginal=False):
    """
    :param memoryPath: path to the file
    :param profile: memory profile (try getProfile first)
    :param checkProfile: if True then gets the profile of the memory before the operation. This is False by default.
    :param showOutput: if True the result of the command is printed. This param takes value False by default.
    :param showOriginal: showOriginal shows the original output returned by volatility.
    :return: list of (probable) hidden processes
    """
    # Get processes:
    res = runVol(memoryPath, 'psxview', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                    checkProfile=checkProfile, added='--apply-rules')

    # Potential hidden processes are not listed in pslist but are listed in psscan
    hidden = [[x.get("PID"),x.get("Name")] for x in res if x.get("pslist")=="False" and x.get("psscan")=="True"
                                                        and x.get("thrdproc")=="True" and len(x.get("ExitTime"))==0]
    return hidden

def getHiddenLibraries(memoryPath, profile=None, checkProfile=False, showOutput=False, showOriginal=False):
    """
    :param memoryPath: path to the file
    :param profile: memory profile (try getProfile first)
    :param checkProfile: if True then gets the profile of the memory before the operation. This is False by default.
    :param showOutput: if True the result of the command is printed. This param takes value False by default.
    :param showOriginal: showOriginal shows the original output returned by volatility.
    :return: list of (probable) hidden DLLs
    """
    # Get modules:
    res = runVol(memoryPath, 'ldrmodules', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                 checkProfile=checkProfile)

    # Potential hidden libraries can be False in the three columns but have a mapped path (VAD)
    hidden = [[x.get("MappedPath"), x.get("Base"), x.get("Pid"), x.get("Process")] for x in res if x.get("InLoad") == "False" and x.get("InInit") == "False"
              and x.get("InMem") == "False" and len(x.get("MappedPath")) > 0]
    return hidden

def getHiddenDrivers(memoryPath, profile=None, checkProfile=False, showOutput=False, showOriginal=False):
    """
    :param memoryPath: path to the file
    :param profile: memory profile (try getProfile first)
    :param checkProfile: if True then gets the profile of the memory before the operation. This is False by default.
    :param showOutput: if True the result of the command is printed. This param takes value False by default.
    :param showOriginal: showOriginal shows the original output returned by volatility.
    :return: list of (probable) hidden drivers
    """
    # Get drivers:
    res_modules = runVol(memoryPath, 'modules', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                         checkProfile=checkProfile)
    res_modscan = runVol(memoryPath, 'modscan', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                         checkProfile=checkProfile)

    list_drivers = [y.get("File") for y in res_modules]

    # Potential hidden drivers are not listed in modules
    hidden = [[x.get("Name"), x.get("File"), x.get("Offset(P)"), x.get("Base"), ] for x in res_modscan if
                            x.get("File") not in list_drivers]
    return hidden

def getRemoteConnections(memoryPath, profile=None, checkProfile=False, showOutput=False, showOriginal=False):
    # Get connections:
    res = runVol(memoryPath, 'connections', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                 checkProfile=checkProfile)

    # Potential hidden libraries can be False in the three columns but have a mapped path (VAD)
    remote = [[x.get("Pid"), x.get("Local Address"), x.get("Remote Address")] for x in res]

    return remote

def getNumberSymbol(symbol):
    """
    :param symbol: symbol to be interpreted
    :return: (max, min)
    """
    if symbol == '+': return (1, sys.maxsize)
    elif symbol == '*': return (0, sys.maxsize)
    elif symbol == '1': return (1,1)
    elif symbol == '0/1': return (0,1)
    elif symbol == '1l': return (1,1)
    elif symbol == '2+': return (2, sys.maxsize)
    elif symbol == '5+': return (5, sys.maxsize)
    else: return (0,0)

def getBehaviour(operating_system):
    """
    Take this method carefully. This information has been structured considering the SANS DFIR posters.
    The value in 'instances' represent:
            + : 1 or more
            * : zero or more
            1 : one
          0/1 : zero or one
           1l : 1 per interactively logged-on user
           x+ : x or more, e.g. 2+ is 2 or more, 5+ is 5 or more
    :param operating_system: operating system chosen
    :return: dictionary with information about the processes in the operating system.
    """
    [name, parent, instances, user_account, start_time, path] = ['name', 'parent', 'instances', 'user_account',
                                                    'start_time', 'path']
    systemRoot = 'C:\\Windows'
    [system32path, iexplorerPath1, iexplorerPath2, explorerPath] = ['%s\\System32\\' % systemRoot,
                                                                    '\\Program Files\\Internet Explorer\\',
                                                                    '\\Program Files (x86)\\Internet Explorer\\',
                                                                    '%s\\' % systemRoot]
    # General behaviour for a Windows 7 system
    System = {name:'System', parent:None, instances:'1', user_account:'Local System', start_time:'Boot',
                     path:None}
    smss = {name:'smss.exe', parent:System.get(name), instances: '1', user_account: 'Local System',
                     start_time: 'Boot, after master', path:system32path}
    wininit = {name:'wininit.exe', parent: [smss.get(name), None], instances: '1', user_account: 'Local System',
                     start_time: 'Boot', path:system32path}
    services = {name: 'services.exe', parent: wininit.get(name), instances: '1', user_account: 'Local System',
                    start_time: 'Boot, after first and second instansces', path: system32path}
    taskhost = {name:'taskhost.exe', parent:services.get(name), instances: '+', user_account: 'Multiple',
                     start_time: 'Variable', path:system32path}
    lsass = {name:'lsass.exe', parent:wininit.get(name), instances: '1', user_account: 'Local System',
                     start_time: 'Boot', path:system32path}
    winlogon = {name: 'winlogon.exe', parent: [smss.get(name), None], instances: '+', user_account: 'Local System',
                    start_time: 'Boot, after first instance', path:system32path}
    explorer = {name: 'explorer.exe', parent:['userinit.exe', None], instances: '1l',
                    user_account: ['Logged-on user(s)'], start_time: 'After the owner\'s interactive session',
                    path: explorerPath}
    iexplore = {name: 'iexplore.exe', parent: explorer.get(name), instances: '*', user_account: 'Logged-on user(s)',
                    start_time: 'When user starts Internet Explorer', path:[iexplorerPath1, iexplorerPath2]}
    csrss = {name: 'csrss.exe', parent: [smss.get(name), None], instances: '2+', user_account: 'Local System',
                    start_time: 'Boot', path:system32path}
    svchost = {name: 'svchost.exe', parent:services.get(name), instances: '5+',
                   user_account: ['Local System', 'Network Service', 'Local Service'], start_time: 'Boot',
                   path: system32path}
    lsm = {name: 'lsm.exe', parent: wininit.get(name), instances: '1', user_account: ['Local System'],
               start_time: 'Boot', path: system32path}

    behaviour = {'System':System, smss.get(name):smss, wininit.get(name):wininit, services.get(name):services,
                 taskhost.get(name):taskhost, lsass.get(name):lsass, winlogon.get(name):winlogon,
                 iexplore.get(name):iexplore, csrss.get(name):csrss, svchost.get(name):svchost,
                 lsm.get(name):lsm, explorer.get(name):explorer}

    if operating_system == 'WIN10':
        # Add special process to the context:
        runtimebroker = {name: 'RuntimeBroker.exe', parent: svchost.get(name), instances: '+',
                    user_account: ['Logged-on user(s)'], start_time: 'Variable', path: system32path}
        lsaiso = {name: 'lsaiso.exe', parent: wininit.get(name), instances: '0/1',
                         user_account: ['Local System'], start_time: 'Boot', path: system32path}

        behaviour.update({runtimebroker.get(name):runtimebroker})
        behaviour.update({lsaiso.get(name):lsaiso})

    #if operating_system == 'WINXP':

    return behaviour


def parseBehaviour(resRunVol):
    """
    :param res: result of runVol for pslist
    :return: new structure of res similar to the output of getBehaviour
    """
    [name, parent, instances, user_account, start_time, path] = ['name', 'parent', 'instances', 'user_account',
                                                                 'start_time', 'path']
    res = []
    for p in resRunVol:
        # Get parent name:
        ppid = p.get('PPID')
        parent_name = [x.get('Name') for x in resRunVol if x.get('PID')==ppid]
        parent_name = parent[0]

        # Get number of instances
        num_i = len([x for x in resRunVol if x.get('Name')==p.get('Name')])

        linp = {name:p.get('Name'), parent:parent_name, instances:num_i, user_account:' ', start_time:' ',
                     path:None}
        res += [linp]

    return res


def getPotentialRogueProcesses(memoryPath, profile=None, checkProfile=False, showOutput=False, showOriginal=False,
                               os_code = 'WINXP'):
    """
    Considers the usual known characteristics of an operating system to identify possible rogue processes.
    Note that this method also returns the 'inocent'
    :return: Structure with a list of potential rogue processes
    """
    rogue = []
    behaviour = getBehaviour(os_code)
    if len(behaviour) == 0: return []

    # Get list of processes:
    res = runVol(memoryPath, 'pslist', profile=profile, showOutput=showOutput, showOriginal=showOriginal,
                 checkProfile=checkProfile)

    # Parse behaviour:
    res = parseBehaviour(res)

    # Check if any process do not satisfy the conditions...
    for p in behaviour:
        # Get the state of all the processes with this name
        current_system_p = [x for x in res if x.get('Name')==p]

        # Get info process:
        p_info = behaviour[p]
        expected_instances = getNumberSymbol(p_info.get('instances'))
        expected_parent = p_info.get('parent')

        # Check known issues: #path = cp.get('path') not checked!!
        for cp in current_system_p:
            if expected_instances[0] <= cp.get('instances') <= expected_instances[1] \
                    or expected_parent != cp.get('parent'):
                rogue += [current_system_p]

    return rogue


def checkProfile(path, extensions = ['.dump', '.bin']):
    """
    Checks for memory profiles.
    :param path: path to the memories.
    :return: profiles for the memories in a dictionary.
    """
    profiles = {}

    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = "%s/%s" % (root, filename)
            extension = os.path.splitext(filepath)[1]
            if extension in extensions:
                # Process memory:
                profile = getProfile(filepath)
                if profile is not None and len(profile)>0:
                    profiles.update({filename:profile})
    return profiles


def checkHidden(path, avoid = [], processes=True, dlls=True, drivers=True, checkProfile=True,
                extensions = ['.dump', '.bin', '.raw'], output_report='reportHidden.txt'):
    """
    Checks for hidden processes in the memory files in a Path (list of memory dumps)
    :param path: path to the memories.
    :param avoid: list of name of files to be omitted ([] by default).
    :param processes: if True (by default) checks (potential) hidden processes
    :param dlls: if True (by default) checks (potential) hidden DLLs
    :param drivers: if True (by default) checks (potential) hidden Drivers
    :param checkProfile: if True (by default) also checks the profile of the memory first.
    :param extensions: extensions for memory files (.dump, .bin and .raw by default)
    :param output_report: name of the file for the results in a report.
    :return: print the results. If report is not 'None' prints the results in a file.
    """
    hiddenProc = []
    hiddenDll = []
    hiddenDrivers = []

    # Print results:
    report_required = output_report is not None
    if report_required:
        orig_stdout = sys.stdout
        f = open(output_report, 'w')
        sys.stdout = f

    # Print in the report the results of the calls
    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = "%s/%s" % (root, filename)
            extension = os.path.splitext(filepath)[1]
            if extension in extensions and filename not in avoid:
                # Process memory:
                if report_required:
                    print('====================\n CHECKS IN MEMORY %s\n====================' % filename)

                if processes:
                    hiddenProc = getHiddenProcesses(filepath, checkProfile=checkProfile, showOriginal=report_required)
                    totP = len(hiddenProc)
                else: totP = '[Not checked]'

                if dlls:
                    hiddenDll = getHiddenLibraries(filepath, checkProfile=checkProfile, showOriginal=report_required)
                    totD = len(hiddenDll)
                else: totD = '[Not checked]'

                if drivers:
                    hiddenDrivers = getHiddenDrivers(filepath, checkProfile=checkProfile, showOriginal=report_required)
                    totDr = len(hiddenDrivers)
                else:
                    totDr = '[Not checked]'

                # Print results
                print('------------ RESULTS MEMORY %s' % filename)
                print('* %s hidden processes' % totP)
                for p in hiddenProc:
                    print('     Name: %s, PID: %s' % (p[0], p[1]))
                print('* %s Hidden DLLs' % totD)
                for p in hiddenDll:
                    print('     Mapped Path: %s, Process: %s (%s)' % (p[0], p[3], p[2]))
                print('* %s Hidden Drivers' % totDr)
                for p in hiddenDrivers:
                    print('     Name: %s, File: %s, Offset:%s, Base:%s' % (p[0], p[1], p[2], p[3]))

    if report_required:
        sys.stdout = orig_stdout
        f.close()

    return True


def printEprocessList(memoryPath, profile=None):
    # create a temporary directory
    with tempfile.TemporaryDirectory() as directory:
        print('- Temporal folder: %s' % directory)

        # Get list of proccess according psxview
        procinfo = {}

        # 1) potential hidden processes - just in case
        print('- Get potential hidden processes ...')
        res = runVol(memoryPath, 'psxview', profile=profile)
        hidden = [x.get("PID") for x in res if x.get("pslist") == "False" and x.get("psscan") == "True"
                  and x.get("thrdproc") == "True" and len(x.get("ExitTime")) == 0]

        for x in res:
            xhidden = x in hidden
            procinfo.update({x.get("PID"):{'pid':x.get("PID"), 'name':x.get("Name"), 'Offset(P)':x.get("Offset(P)"),
                                           'hidden':xhidden}})

        # 2) get the offset for the processes - some we know, some others we don't
        print('- Calculating offset (virtual) for the processes...')

        res = runVol(memoryPath, 'pslist', profile=profile, showOutput=False)

        for x in res:
            pid = x.get("PID")
            p = procinfo.get(pid)
            if p:
                offset = x.get("Offset(V)")
            else: #the process is hidden, find offset in a diffent way, perhaps a dump
                ad = '-o %s -D %s' % (pid, directory)
                resdump = runVol(memoryPath, 'procdump', profile=profile, showOutput=True, added=ad)
                offset = resdump.get("Process(V)")

            p.update({'Offset(V)':offset})

            # 3) Go to E_PROCESS
            print('- Go to E_PROCESS pid:%s, name:%s, offset(V):%s' % (pid, p.get("name"), p.get("Offset(V)")))
            resvol = runVol(memoryPath, 'volshell', profile=profile, showOutput=True, showOriginal=True)

            print(resvol)
            procinfo.update({pid:p})

        # print all
        pprint.pprint(procinfo)

        #remove dir
        shutil.rmtree(directory)



#-----------------------------------------
#       MAIN
#-----------------------------------------
if __name__ == '__main__':
    memoryPath = 'sources/mem'
    memory = "%s/sample001.bin" % memoryPath
    profile = "WinXPSP2x86"
    corrupt = ['sample005.bin', 'sample002.bin'] #known corrupted memories
    """
    Example: python3 eatingMemory.py sources/mem
    
    import eatingMemory
    memoryPath = 'sources/mem'
    memory = "%s/sample001.bin" % memoryPath
    profile = "WinXPSP2x86"
    eatingMemory.printEprocessList(memory, profile=profile)
    """

    #getSample()
    #profile = getProfile(memory, showOutput=True)
    #profile = 'WinXPSP2x86'
    #processes = getProcesses(memory, profile=profile, showOutput=False, listPID=True)
    #res = runVol(memory, 'psscan', profile=profile, showOutput=False, listPID=True)

    options = ["Check hidden", "Beauty E_PROCESS list"]
    max_options = len(options)

    if len(sys.argv) > 1:
        memory = sys.argv[1]
        if not aux.checkExtension(memory, extensions=["dmp", "raw"]):
            # Ask for file:
            memory = aux.getPathToFile(msg='Please, provide a valid file:',file_type='.dmp/.raw')
    else:
        # Ask for file:
        #memory = aux.getPathToFile(type_file='.dmp/.raw')
        # use default
        print('Default memory file: %s, and memory path: %s' % (memory, memoryPath))

    # Show options:
    ans = aux.showOptions(options)

    while ans <= max_options:
        if ans == 1: # check hidden
            print('Checking hidden... be patient, this can take several minutes... ')
            res = checkHidden(memoryPath, avoid=corrupt, checkProfile=False, output_report='tmp/reportHidden.txt')

        if ans == 2: # e_process beauty
            #sample003 is useful for this
            print('Printing beauty E_PROCESS list')
            printEprocessList(memory, profile)



