'''
 *  Project             :   Screenipy
 *  Author              :   Pranjal Joshi
 *  Created             :   21/04/2021
 *  Description         :   Class for handling OTA updates
'''

from classes.ColorText import colorText
import requests
import os
import platform
import sys
import subprocess
import requests
from classes import VERSION
from classes.log import default_logger

class OTAUpdater:

    developmentVersion = 'd'

    # Download and replace exe through other process for Windows
    def updateForWindows(url):
        batFile = """@echo off
color a
echo [+] pkscreener Software Updater!
echo [+] Downloading Software Update...
echo [+] This may take some time as per your Internet Speed, Please Wait...
curl -o pkscreener.exe -L """ + url + """
echo [+] Newly downloaded file saved in %cd%
echo [+] Software Update Completed! Run'pkscreener.exe' again as usual to continue..
pause
del updater.bat & exit
        """
        f = open("updater.bat",'w')
        f.write(batFile)
        f.close()
        subprocess.Popen('start updater.bat', shell=True)
        sys.exit(0)

    # Download and replace bin through other process for Linux
    def updateForLinux(url):
        bashFile = """#!/bin/bash
echo ""
echo "[+] Starting PKScreener updater, Please Wait..."
sleep 3
echo "[+] pkscreener Software Updater!"
echo "[+] Downloading Software Update..."
echo "[+] This may take some time as per your Internet Speed, Please Wait..."
wget -q """ + url + """ -O pkscreener.bin
echo "[+] Newly downloaded file saved in $(pwd)"
chmod +x pkscreener.bin
echo "[+] Update Completed! Run 'pkscreener.bin' again as usual to continue.."
rm updater.sh
        """
        f = open("updater.sh",'w')
        f.write(bashFile)
        f.close()
        subprocess.Popen('bash updater.sh', shell=True)
        sys.exit(0)

        # Download and replace run through other process for Mac
    def updateForMac(url):
        bashFile = """#!/bin/bash
echo ""
echo "[+] Starting PKScreener updater, Please Wait..."
sleep 3
echo "[+] pkscreener Software Updater!"
echo "[+] Downloading Software Update..."
echo "[+] This may take some time as per your Internet Speed, Please Wait..."
curl -o pkscreener.run -L """ + url + """
echo "[+] Newly downloaded file saved in $(pwd)"
chmod +x pkscreener.run
echo "[+] Update Completed! Run 'pkscreener.run' again as usual to continue.."
rm updater.sh
        """
        f = open("updater.sh",'w')
        f.write(bashFile)
        f.close()
        subprocess.Popen('bash updater.sh', shell=True)
        sys.exit(0)

    # Parse changelog from release.md
    def showWhatsNew():
        url = "https://raw.githubusercontent.com/pkjmesra/PKScreener/main/src/release.md"
        md = requests.get(url)
        txt = md.text
        txt = txt.split("New?")[1]
        txt = txt.split("## Downloads")[0]
        txt = txt.replace('**','').replace('`','').strip()
        return (txt+"\n")

    # Check for update and download if available
    def checkForUpdate(proxyServer, VERSION=VERSION):
        OTAUpdater.checkForUpdate.url = None
        resp = None
        try:
            now = float(VERSION)
            if proxyServer:
                resp = requests.get("https://api.github.com/repos/pkjmesra/PKScreener/releases/latest",proxies={'https':proxyServer})
            else:
                resp = requests.get("https://api.github.com/repos/pkjmesra/PKScreener/releases/latest")
            if 'Windows' in platform.system():
                OTAUpdater.checkForUpdate.url = resp.json()['assets'][1]['browser_download_url']
                size = int(resp.json()['assets'][1]['size']/(1024*1024))
            elif 'Darwin' in platform.system():
                OTAUpdater.checkForUpdate.url = resp.json()['assets'][2]['browser_download_url']
                size = int(resp.json()['assets'][2]['size']/(1024*1024))
            else:
                OTAUpdater.checkForUpdate.url = resp.json()['assets'][0]['browser_download_url']
                size = int(resp.json()['assets'][0]['size']/(1024*1024))
            if(float(resp.json()['tag_name']) > now):
                print(colorText.BOLD + colorText.WARN + "[+] What's New in this Update?\n" + OTAUpdater.showWhatsNew() + colorText.END)
                action = str(input(colorText.BOLD + colorText.WARN + ('\n[+] New Software update (v%s) available. Download Now (Size: %dMB)? [Y/N]: ' % (str(resp.json()['tag_name']),size)))).lower()
                if(action == 'y'):
                    try:
                        if 'Windows' in platform.system():
                            OTAUpdater.updateForWindows(OTAUpdater.checkForUpdate.url)
                        elif 'Darwin' in platform.system():
                            OTAUpdater.updateForMac(OTAUpdater.checkForUpdate.url)
                        else:
                            OTAUpdater.updateForLinux(OTAUpdater.checkForUpdate.url)
                    except Exception as e:
                        default_logger().debug(e, exc_info=True)
                        print(colorText.BOLD + colorText.WARN + '[+] Error occured while updating!' + colorText.END)
                        raise(e)
            elif(float(resp.json()['tag_name']) < now):
                print(colorText.BOLD + colorText.FAIL + ('[+] This version (v%s) is in Development mode and unreleased!' % VERSION) + colorText.END)
                return OTAUpdater.developmentVersion
        except Exception as e:
            default_logger().debug(e, exc_info=True)
            if OTAUpdater.checkForUpdate.url != None:
                print(colorText.BOLD + colorText.BLUE + ("[+] Download update manually from %s\n" % OTAUpdater.checkForUpdate.url) + colorText.END)
            if resp.json()['message'] == 'Not Found':
                OTAUpdater.checkForUpdate.url = 'exe/bin not available.'
                print(colorText.BOLD + colorText.FAIL + "[+] No exe/bin as an update available!" + colorText.END)
            print(colorText.BOLD + colorText.FAIL + "[+] Failure while checking update!" + colorText.END)
            print(e)
        return