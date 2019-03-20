#!/usr/bin/python
# Copyright (c) 2015 Jonathan Struebel <jonathan.struebel@gmail.com>
# Modified for Jellyfin 2019 TurnKey GNU/Linux <jeremy@turnkeylinux.org>
"""Perform initial Jellyfin Media Server setup"""

import sys
# used to load JellyfinTools
sys.path.append('/usr/lib/inithooks/bin')
import JellyfinTools
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
    server = jellyfin.getServer()
    url = "%s/web/login.html" % server
    status = jellyfin.doUtils.downloadUrl(url, json=False, authenticate=False)

    if (status == 302 or status == 'Redirect'):
        # Perform initial Jellyfin setup
        settings = "/etc/jellyfininitsetup"
        try:
            f = open(settings,'r')
        except:
            return

        for line in f:
            fields = line.split('|')
            if '#' in fields[0]:
                continue

            jsonEnc = False
            if (fields[2] == "json"):
                jsonEnc = True
            fields[1] = fields[1].replace("{server}", server, 1)
            fields[1] = fields[1].replace("{user}", jellyfin.getUsername(), 1)
            if len(fields) > 3:
                fields[3] = fields[3].replace("{user}", jellyfin.getUsername(), 1)
                jellyfin.doUtils.downloadUrl(fields[1], postBody=fields[3], type=fields[0], json=jsonEnc, authenticate=False)
            else:
                jellyfin.doUtils.downloadUrl(fields[1], type=fields[0], json=jsonEnc, authenticate=False)

        f.close()

    jellyfin.currPass = oldpw
    jellyfin.authenticate()

    # Perform remaining Jellyfin setup
    settings = "/etc/jellyfinsetup"
    try:
        f = open(settings,'r')
    except:
        return

    for line in f:
        fields = line.split('|')
        if '#' in fields[0]:
            continue

        jsonEnc = False
        if (fields[2] == "json"):
            jsonEnc = True
        fields[1] = fields[1].replace("{server}", server, 1)
        fields[1] = fields[1].replace("{user}", jellyfin.getUsername(), 1)
        if len(fields) > 3:
            fields[3] = fields[3].replace("{user}", jellyfin.getUsername(), 1)
            if jsonEnc:
                fields[3] = json.loads(fields[3])
            jellyfin.doUtils.downloadUrl(fields[1], postBody=fields[3], type=fields[0], json=jsonEnc, authenticate=True)
        else:
            jellyfin.doUtils.downloadUrl(fields[1], type=fields[0], json=jsonEnc, authenticate=True)

    f.close()

if __name__ == "__main__":
    main()

