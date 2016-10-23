#!/usr/bin/env python

from subprocess import *
import textwrap
import shutil
import sys
import os

# TODO: make sure to load mod_wsgi in the httpd.conf file
# TODO: make sure to load the other required modules for the Header, and teh Unset etc

def install_wsgi(apache_dir):
    print "Preparing to install Mod WSGI...\n"

    # removing the mod wsgi source if it exists already
    if os.path.exists("./dependencies/mod_wsgi-4.5.7"):
        shutil.rmtree("./dependencies/mod_wsgi-4.5.7")

    wsgi_so = "{}/modules/mod_wsgi.so".format(apache_dir)
    if os.path.exists(wsgi_so):
        answer = raw_input("Mod WSGI has already been installed. "
                    "\nWould you like to reinstall it? (y/[N]):  ")
        if answer in ['y', 'Y']:
            try:
                os.remove("{}/modules/mod_wsgi.so".format(apache_dir))
                shutil.rmtree("./dependencies/mod_wsgi-4.5.7")
            except: pass
        else: return

    os.chdir('./dependencies')

    wsgi_tar_src = './mod_wsgi-4.5.7.tar.gz'
    wsgi_src = './mod_wsgi-4.5.7'

    print "Un-tarring mod wsgi 4.5.7 source...\n"
    check_call(['tar', '-zxpvf', wsgi_tar_src])

    os.chdir(wsgi_src)

    config = """
    ./configure --with-apxs={apache_dir}/bin/apxs
        --with-python=/usr/bin/python2.7
    """.format(apache_dir=apache_dir)

    print "Running mod wsgi configure...\n"
    check_call(config.strip().split())

    print "Building mod wsgi...\n"
    check_call(['make'])

    print "Installing mod wsgi...\n"
    check_call(['make', 'install'])

    print "Cleaning up mod wsgi source...\n"
    shutil.rmtree('../mod_wsgi-4.5.7')

    print "Mod WSGI installed successfully!\n"


def add_vhost_config(onramp_dir, apache_dir, port):
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

    vhost_config = """
    # CUSTOM SETTINGS FOR ONRAMP

    WSGIScriptAlias / {onramp_dir}/ui/wsgi.py
    WSGIPythonPath {onramp_dir}:{onramp_dir}/virtual-env/lib/python2.7/site-packages
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
                Order allow,deny
                Allow from all
            </Files>
        </Directory>

        # allow django to get our static files
        <Location /static >
            Order allow,deny
            Allow from all
        </Location>

        # limit the type of HTTP methods possible
        <location / >
            AllowMethods GET POST PUT DELETE
        </location>
    </VirtualHost>
    """.format(onramp_dir=onramp_dir, port=port)

    fh = open(vhosts, "a")
    fh.write("\n")
    fh.write(textwrap.dedent(vhost_config))
    fh.close()

    print "\nApache configured successfully!\n"


if __name__ == '__main__':
    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp server directory: ")
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

    # add the required vhost directive to the apache httpd-vhost config
    add_vhost_config(onramp_dir, apache_dir, port)

    answer = raw_input("Do you want to install Mod WSGI (y/N)?: ")
    if answer in ['y', 'Y']:
        install_wsgi(apache_dir)

    print "Please restart your apache to complete the configuration.\n"
