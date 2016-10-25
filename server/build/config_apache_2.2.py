#!/usr/bin/env python

from utils.terminal import TerminalFonts
from subprocess import *
import textwrap
import shutil
import sys
import os

# TODO: test this to make sure it works

# TODO: check if wsgi installs correctly since apache 2.2 needs wsgi.conf
# TODO: and wsgi.load files in mods_available/mods_enabled directories?


def install_wsgi(TF, apache_dir):
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

    print TF.format("Mod WSGI installed successfully!\n", 1)


def configure_vhost_conf(TF, onramp_dir, apache_dir, port):
    print "Preparing to configure virtual hosts file...\n"

    # strip off any trailing slashes so we have clean paths in the config
    if onramp_dir.endswith("/"):
        onramp_dir = onramp_dir[:-1]

    # strip off any trailing slashes so we have clean paths in the config
    if apache_dir.endswith("/"):
        apache_dir = apache_dir[:-1]

    # NOTE: the default apache 2.2 virtual hosts file should be the following
    default_vhosts = "{}/sites-available/default".format(apache_dir)

    # ask the user to configure the default virtual host file or enter in the correct one
    vhosts = raw_input("Press enter to configure the default virtual host file at ({})\n"
              "Or enter in the full path to your virtual host file: ".format(default_vhosts))
    vhosts = vhosts.strip() or default_vhosts
    if not os.path.exists(vhosts):
        print "\n{}: There is no virtual host file at the following " \
              "path: {}\n".format(TF.format("ERROR", 4), vhosts)
        sys.exit(1)

    fh = open(vhosts, "r")
    for line in fh.readlines():
        if ":{}".format(port) in line:
            print "{}: The virtual hosts file already contains an entry for that port!".format(TF.format("ERROR", 4))
            print "If you would like to run OnRamp under the port ({}) please remove the\n" \
                  "current configuration for that port from your enabled virtual hosts file\n" \
                  "and then re-run this script to configure your Apache 2.2 webserver for OnRamp.\n".format(port)
            sys.exit(1)
    fh.close()

    vhost_config = """
    # CUSTOM SETTINGS FOR ONRAMP

    WSGIScriptAlias / {onramp_dir}/ui/wsgi.py
    WSGIPythonPath {onramp_dir}:{onramp_dir}/virtual-env/lib/python2.7/site-packages
    Alias /static {onramp_dir}/ui/static

    <VirtualHost *:{port}>
        ServerAlias *.onramp.com

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

    print TF.format("Apache's virtual hosts file was configured successfully!\n", 1)


def configure_httpd_conf(TF, apache_dir, port_num):
    print "Preparing to configure httpd.conf...\n"

    httpd_conf = "{}/httpd.conf".format(apache_dir)
    if not os.path.exists(httpd_conf):
        print "\n{}: Unable to find httpd.conf at the default location.\n".format(TF.format('WARNING', 3))
        httpd_conf = raw_input("\nPlease enter in the full path to your httpd.conf file: ")
        if not os.path.exists(httpd_conf):
            print "\n{}: There is no httpd.conf at the following " \
                  "path: {}\n".format(TF.format("ERROR", 4), httpd_conf)
            sys.exit(1)

    module = False
    port = False

    with open(httpd_conf, 'r') as fh:
        text = fh.read()
        if "LoadModule wsgi_module" in text:
            print "Apache is already loading the WSGI Module!\n"
            module = True
        if "Listen {}".format(port) in text:
            print "Apache is already listening on that port!\n"
            port = True

    fh = open(httpd_conf, "a")
    if not port or not module:
        fh.write("# Custom settings for the OnRamp to Parallel Computing project\n")
        if not module:
            fh.write("LoadModule wsgi_module modules/mod_wsgi.so\n")
        if not port:
            fh.write("Listen {}\n".format(port_num))

    print TF.format("Apache's httpd.conf was configured successfully!\n", 1)


if __name__ == '__main__':
    # create an instance of our Terminal Fonts class to help with printing
    TF = TerminalFonts()

    # check to make sure we have root permissions to execute the script
    # since we need those permissions to install dependencies through yum
    if os.getuid() != 0:
        print '\n{}: Please run this script with "sudo" or as the ' \
              'root user.\n'.format(TF.format("Permission Error", 4))
        sys.exit(0)

    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp server directory: ")
    if not onramp_dir.startswith("/") and not os.path.isdir(onramp_dir):
        print "Please enter in a valid directory path!"
        sys.exit(1)

    apache_dir = raw_input("\nPlease enter in the full path to your apache 2.4 directory: ")
    if not apache_dir.startswith("/") and not os.path.isdir(apache_dir):
        print "Please enter in a valid directory path!"
        sys.exit(1)

    port = raw_input("\nPlease enter in the port you wish to run OnRamp under (80): ")
    port = port or "80"
    if not port.isdigit():
        print "Please enter in a valid port!"
        sys.exit(1)

    print  # Just printing a blank line here for space

    # add the required vhost directive to the apache httpd-vhost config
    configure_vhost_conf(TF, onramp_dir, apache_dir, port)
    configure_httpd_conf(TF, apache_dir, port)
    install_wsgi(TF, apache_dir)

    print TF.format("\nPlease restart your apache to complete the configuration.\n", 1)
