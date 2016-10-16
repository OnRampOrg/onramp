#!/usr/bin/env python

import sys
import os

vhost_config = """
WSGIScriptAlias / {onramp_dir}/ui/wsgi.py
WSGIPythonPath {onramp_dir}/ui:{onramp_dir}/virtual-env/lib/python2.7/site-packages
Alias /static {onramp_dir}/ui/static

<VirtualHost *:{port}>
    RewriteEngine On
    RewriteCond %{{REQUEST_METHOD}} ^TRACE
    RewriteRule .* - [F]

    ServerAlias *.onramp.com

    # disable ETag because it's inefficient and will make
    # it so the browser won't cache our static files
    Header unset ETag
    FileETag None

    # make sure the browser accepts all encodings
    Header append Vary: Accept-Encoding

    DocumentRoot {onramp_dir}/ui/

    <Directory {onramp_dir}/ui/ >
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # allow django to get our static files
    <Location /static >
        Require all granted
    </Location>

    # limit the type of HTTP methods possible
    <location / >
        AllowMethods GET POST PUT DELETE
    </location>
</VirtualHost>
"""

def main(onramp_dir, apache_dir, port):
    # strip off any trailing slashes so we have clean paths in the config
    if onramp_dir.endswith("/"):
        onramp_dir = onramp_dir[:-1]

    # strip off any trailing slashes so we have clean paths in the config
    if apache_dir.endswith("/"):
        apache_dir = apache_dir[:-1]

    vhosts = "{}/conf/extra/httpd-vhosts.conf".format(apache_dir)
    if not os.path.exists(vhosts):
        print "Unable to find httpd-vhosts.conf file at: {}".format(vhosts)
        sys.exit(1)

    fh = open(vhosts, "r")
    for line in fh.readlines():
        if ":{}".format(port) in line:
            print "The virtual hosts file already contains an entry for that port!"
            sys.exit(1)
    fh.close()

    fh = open(vhosts, "a")
    fh.write("\n")
    fh.write(vhost_config.format(onramp_dir=onramp_dir, port=port))
    fh.close()

    print "\nApache configured successfully!\n"
    print "Please restart apache to complete configuration.\n"

if __name__ == '__main__':
    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp directory: ")
    if not onramp_dir.startswith("/") and not os.path.isdir(onramp_dir):
        print "Please enter in a valid path!"
        sys.exit(1)

    apache_dir = raw_input("\nPlease enter in the full path to your apache 2.4 \n"
               "directory or use the default ({}/webserver): ".format(onramp_dir.rstrip("/")))
    apache_dir = apache_dir or "{}/webserver/".format(onramp_dir.rstrip("/"))
    if not apache_dir.startswith("/") and not os.path.isdir(apache_dir):
        print "Please enter in a valid path!"
        sys.exit(1)

    port = raw_input("\nPlease enter in the port you wish to run OnRamp under (80): ")
    port = port or "80"
    if not port.isdigit():
        print "Please enter in a valid port!"
        sys.exit(1)

    main(onramp_dir, apache_dir, port)
