#!/usr/bin/python
"""Set MediaWiki admin password

Option:
    --pass=     unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
"""

import re
import sys
import getopt
import hashlib
import inithooks_cache
import subprocess

from dialog_wrapper import Dialog
from mysqlconf import MySQL

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

DEFAULT_DOMAIN="www.example.com"

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ['help', 'pass=', 'domain='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    domain = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
            if password.lower() == "admin":
                usage("illegal password specified")
        elif opt == '--domain':
            domain = val

    if not password:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')
        while True:
            password = d.get_password(
                "MediaWiki Password",
                "Enter new password for the MediaWiki 'admin' account.")

            if password.lower() == "admin":
                d.error("Illegal password, please try again.")
                continue

            break

    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "MediaWiki Domain",
            "Enter the domain to serve MediaWiki",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    fqdn = re.compile(r"https?://")
    fqdn = fqdn.sub('', domain).strip('/')
    domain = "https://%s/" % fqdn

    inithooks_cache.write("APP_DOMAIN", domain)

    hashpass = hashlib.md5(password).hexdigest()
    hashpass = hashlib.md5("1-" + hashpass).hexdigest()     # userid 1

    m = MySQL()
    m.execute('UPDATE mediawiki.user SET user_password=\"%s\" WHERE user_id=\"1\";' % hashpass)

    subprocess.call(['sed', '-i',
            '\|^\$wgServer|s|=.*|= "https://%s";|' % fqdn,
            '/var/www/mediawiki/LocalSettings.php'])
    subprocess.call(['sed', '-i',
            '\|RewriteRule|s|https://.*|https://%s/\$1 [R,L]|' % fqdn,
            '/etc/apache2/sites-available/mediawiki.conf'])
    subprocess.call(['service', 'apache2', 'restart'])

if __name__ == "__main__":
    main()

