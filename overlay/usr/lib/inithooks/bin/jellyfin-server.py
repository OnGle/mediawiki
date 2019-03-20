#!/usr/bin/python
# Copyright (c) 2015 Jonathan Struebel <jonathan.struebel@gmail.com>
# Modified for Jellyfin 2019 TurnKey GNU/Linux <jeremy@turnkeylinux.org>
"""Configure Jellyfin Media Server

Arguments:
    none

Options:
    -p --pass=    if not provided, will ask interactively
"""

import sys
import getopt
import signal
import JellyfinTools
from JellyfinTools import UserClient
import json

def fatal(s):
    print >> sys.stderr, "Error:", s
    sys.exit(1)

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hp:", ['help', 'pass='])
    except getopt.GetoptError, e:
        usage(e)

    jellyfin = UserClient()

    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-p', '--pass'):
            password = val

    if not password:
        from dialog_wrapper import Dialog
        d = Dialog('TurnKey GNU/Linux - First boot configuration')
        password = d.get_password(
            "Jellyfin User Password",
            "Please enter new password for the Jellyfin Server %s account." % jellyfin.getUsername())

    pwfile = "/etc/jellyfinpass"
    oldpw = None
    try:
        f = open(pwfile,'r')
    except:
        oldpw = ""
    else:
        oldpw = f.readline().rstrip('\r\n')
        f.close()

    server = jellyfin.getServer()
    url = "%s/web/login.html" % server
    jellyfin.currPass = oldpw
    jellyfin.authenticate()

    # Change default user password
    url = "{server}/emby/Users/%s/Password" % jellyfin.getUserId()
    data = json.loads("{\"CurrentPassword\":\"%s\",\"NewPw\":\"%s\"}" % (jellyfin.hashPassword(oldpw), password))
    jellyfin.doUtils.downloadUrl(url, postBody=data, type="POST", json=True, authenticate=True)

    # Remove device
    url = "{server}/emby/Devices?Id=%s" % jellyfin.doUtils.deviceId
    jellyfin.doUtils.downloadUrl(url, type="DELETE", json=False, authenticate=True)

if __name__ == "__main__":
    main()

