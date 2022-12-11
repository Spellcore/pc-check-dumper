#Imports
import psutil
from os.path import isfile, join
from os import listdir
import os
import requests
import subprocess
import json
import time
import shutil


strings2Url = 'https://github.com/glmcdona/strings2/raw/master/x64/Release/strings.exe'

class Dumper(object):
    def __init__(self):
        super(Dumper, self).__init__()
        self.user_path = '/'.join(os.getcwd().split('\\', 3)[:3])
        self.drive_letter = os.getcwd().split('\\', 1)[0]+'/'
        self.winUsername = os.getlogin()

    def dependencies(self):
        path = f'{self.drive_letter}/Windows/Temp/Abyss'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(f'{path}/strings2.exe', 'wb') as f:
            f.write(requests.get(strings2Url).content)


    def getPID(self, name, service=False):
        pid = 0
        if service:
            response = str(subprocess.check_output(f'tasklist /svc /FI "Services eq {name}')).split('\\r\\n')
            for process in response:
                if name in process:
                    pid = process.split()[1]
                    return pid
        else:
            pid = [p.pid for p in psutil.process_iter(attrs=['pid', 'name']) if name == p.name()][0]
            return pid

    def dump(self, pid):
        cmd = f'{self.drive_letter}/Windows/Temp/Abyss/strings2.exe -pid {pid} -raw -nh'
        strings = str(subprocess.check_output(cmd)).replace("\\\\","/")
        strings = list(set(strings.split("\\r\\n")))

        return strings    
            
    def robloxProcess(self):
        robloxProcess_info = {}
        self.robloxRunning = True

        #Get processes with the name "RobloxPlayerBeta"
        process = [p for p in psutil.process_iter(attrs=['pid', 'name']) if 'RobloxPlayerBeta' in p.info['name']]
        if process:
            process = process[0]
            pid = process.info['pid']
            print(f'Roblox found on PID: {pid}')
            self.robloxRunning = True
        else:
            input(f'Roblox not found...\nPress enter to continue')
            self.robloxRunning = False
  
        if self.robloxRunning:
            self.RobloxPlayerBetaPid = pid
   

    def modificationTimes(self):
        SID = str(subprocess.check_output(f'wmic useraccount where name="{self.winUsername}" get sid')).split('\\r\\r\\n')[1]
        recycle_bin_path = self.drive_letter+"/$Recycle.Bin/"+SID

        f = open("modification_times.txt","a")
        #Recycle Bin Path
        modTime = os.path.getmtime(recycle_bin_path)
        modTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTime))
        f.write(f'    Recycle Bin: {modTime}\n')

        #Explorer Start Time
        pid = self.getPID('explorer.exe')
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.Process(pid).create_time()))
        f.write(f'    Explorer: {startTime}\n')
        
        
        #RobloxPlayerBeta Start Time
        if self.robloxRunning:
            startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.Process(self.RobloxPlayerBetaPid).create_time()))
            f.write(f'    Roblox: {startTime}')
        else:
            f.write("Roblox not running\n")



    #Prints executed programs to dps.txt
    def printDPS(self):
        f = open("dps.txt", "a")
        processId = self.getPID("DPS", service=True)
        if processId == 0:
            f.write("DPS not running")
            f.close()
            return
        else:
            strings = self.dump(processId)
            for string in strings:
                if '!!' in string:
                    f.write(string + '\n')
        f.close()
        return
  
    def printPcaClient(self):
        f = open("pcaclient.txt", "a")
        pid = self.getPID("explorer.exe")
        if pid == 0:
            f.write("PCAClient not running")
            f.close()
            return
        else:
            strings = self.dump(pid)
            for x in strings:
                if 'PcaClient' in x:
                    x = x.split('\r')
                    for proc in x:
                        f.write(proc + '\n')
            f.close()
            return

    def printDll(self):
        f = open("dll.txt","a")
        if not self.robloxRunning:
            f.write("Roblox not running")
            f.close()
            return
        else:
            processId = self.getPID("RobloxPlayerBeta.exe")
            f = open('dll.txt', 'a')

            p = psutil.Process(processId)

            for path in p.memory_maps():
                dll = path[0].split('\\')[3]
                if 'dll' in dll:
                    f.write(dll + '\n')

            f.close()

    
if __name__ == "__main__":
    ddump = Dumper()
    ddump.dependencies()
    ddump.robloxProcess()
    ddump.printDll()
    ddump.printDPS()
    ddump.printPcaClient()
    ddump.modificationTimes()


    input('\nFinished!\nPress enter to exit..')

    temp = f'{ddump.drive_letter}/Windows/Temp/Abyss'
    if os.path.exists(temp):
        shutil.rmtree(temp)