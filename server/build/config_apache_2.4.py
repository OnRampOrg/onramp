from utils.terminal import TerminalFonts
from subprocess import *
import textwrap
import sys
import os


def validate_path(path, filename=None, remove_slash=False):
    if filename is not None:
        if os.path.exists(path) and path.endswith(filename):
            print
            return path if not remove_slash else path.rstrip("/")
    while not os.path.exists(path):
        print "Nothing at the following path exists: %s\n" % path
        path = raw_input("Please enter in a valid path for the %s file: " % file)
        answer = raw_input("Is the following path correct? (%s) (y/N): " % path)
        if answer in ['y', 'Y'] and os.path.exists(path):
            if filename is None:
                break
            elif path.endswith(filename):
                break
            else:
                continue
        print
    return path if not remove_slash else path.rstrip("/")


def install_wsgi(TF, modules_dir):
    print "Preparing to install Mod WSGI...\n"

    wsgi_so = "%s/mod_wsgi.so" % modules_dir
    if os.path.exists(wsgi_so):
        answer = raw_input("Mod WSGI has already been installed. "
                    "\nWould you like to reinstall it? (y/[N]):  ")
        if answer in ['y', 'Y']:
            try:
                check_call(['sudo', 'rm', '-f', wsgi_so])
                check_call(['sudo', 'rm', '-rf', './dependencies/mod_wsgi-4.5.7'])
            except:
                pass
        else:
            return

    # change to the dependency directory to build mod WSGI
    os.chdir('./dependencies')

    # un-tar mod wsgi source so we can build it manually
    wsgi_tar_src = './mod_wsgi-4.5.7.tar.gz'
    wsgi_src = './mod_wsgi-4.5.7'
    print "Un-tarring mod wsgi 4.5.7 source...\n"
    check_call(['sudo', 'tar', '-zxpvf', wsgi_tar_src])

    # change to the un-tarred mod wsgi directory
    os.chdir(wsgi_src)

    print "Running mod wsgi configure...\n"
    # apparently the configure script will find the apxs executable
    # automatically if apache is installed in a findable location
    check_call(['sudo', './configure', '--with-python=%s' % sys.executable])

    print "Building mod wsgi...\n"
    check_call(['sudo', 'make'])

    print "Installing mod wsgi...\n"
    check_call(['sudo', 'make', 'install'])

    print "Cleaning up mod wsgi source...\n"
    check_call(['sudo', 'rm', '-rf', '../mod_wsgi-4.5.7'])

    print "Making symlinks for python for Mod WSGI..."

    print 'If you don\'t know the path to the following files try using the "locate" command\n'

    link_1 = raw_input("Please enter in the full path to your libpython2.7.so.1.0 file: ")
    link_1 = validate_path(link_1, filename='libpython2.7.so.1.0', remove_slash=True)
    if not link_1.startswith("/usr/lib64"):
        check_call(['sudo', 'ln', '-s', link_1, '/usr/lib64'])

    link_2 = raw_input("Please enter in the full path to your libpython2.7.so file: ")
    link_2 = validate_path(link_2, filename='libpython2.7.so', remove_slash=True)
    if not link_2.startswith("/usr/"):
        check_call(['sudo', 'ln', '-s', link_2, '/usr/'])

    print TF.format("Mod WSGI installed successfully!\n", 1)


def configure_vhost_conf(TF, onramp_dir, apache_dir, port):
    print "Preparing to configure virtual hosts file...\n"

    vhosts_path = "{}/conf/extra/httpd-vhosts.conf".format(apache_dir)
    if not os.path.exists(vhosts_path):
        print "\n{}: Unable to find httpd-vhosts.conf at the default location.\n".format(TF.format('WARNING', 3))
        # get the full path to the httpd.conf file so we can append our OnRamp configuration
        vhosts_path = raw_input("Please enter in the full path to your httpd-vhosts.conf: ")
        vhosts_path = validate_path(vhosts_path, filename="httpd-vhosts.conf")

    vhost_config = []
    fh = open(vhosts_path, "r")
    for line in fh.readlines():
        vhost_config.append(line)
        if ":%s" % port in line:
            print "{}: The virtual hosts file already contains an entry for that port!".format(TF.format("ERROR", 4))
            print "If you would like to run OnRamp under the port ({}) please remove the\n" \
                  "current configuration for that port from your httpd-vhosts.conf file\n" \
                  "and then re-run this script to configure your Apache 2.4 webserver for OnRamp.\n".format(port)
            sys.exit(1)
    fh.close()

    onramp_config = """
    # CUSTOM SETTINGS FOR ONRAMP

    WSGIScriptAlias / {onramp_dir}/ui/wsgi.py
    WSGIPythonPath {onramp_dir}:{onramp_dir}/virtual-env/lib/python2.7/site-packages
    Alias /static {onramp_dir}/ui/static

    <VirtualHost *:{port}>
        ServerAlias *.onramp.com

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
    """.format(onramp_dir=onramp_dir, port=port)

    # write out the new lines to a temp file to copy over with sudo
    with open("/tmp/httpd_conf", "w") as fh:
        vhost_config += "".join(textwrap.dedent(onramp_config))
        fh.writelines(vhost_config)
    # write over the /etc/environment file with the new lines from the tmp file
    check_call(['sudo', 'cp', '/tmp/httpd_vhosts_conf', vhosts_path])
    # remove the temporary file that was created
    check_call(['sudo', 'rm', '-f', '/tmp/httpd_vhosts_conf'])

    print TF.format("Apache's virtual hosts file was configured successfully!\n", 1)


def configure_httpd_conf(TF, apache_dir, port_num):
    print "Preparing to configure httpd.conf...\n"

    httpd_path = "{}/conf/httpd.conf".format(apache_dir)
    if not os.path.exists(httpd_path):
        print "\n{}: Unable to find httpd.conf at the default location.\n".format(TF.format('WARNING', 3))
        # get the full path to the httpd.conf file so we can append our OnRamp configuration
        httpd_path = raw_input("Please enter in the full path to your httpd.conf: ")
        httpd_path = validate_path(httpd_path, filename="httpd.conf")

    httpd_config = []
    module = False  # flag to determine if we need to load mod wsgi in the httpd.conf
    port = False  # flag to determine if we need to listen on a port in the httpd.conf

    with open(httpd_path, 'r') as fh:
        for line in fh.readlines():
            httpd_config.append(line)
            if "LoadModule wsgi_module" in line:
                print "Apache is already loading the WSGI Module!\n"
                module = True
            if "Listen {}".format(port) in line:
                print "Apache is already listening on that port!\n"
                port = True

    # write out the new lines to a temp file to copy over with sudo
    with open("/tmp/httpd_conf", "w") as fh:
        if not port or not module:
            httpd_config.append("# CUSTOM SETTINGS FOR ONRAMP\n")
            if not module:
                httpd_config.append("LoadModule wsgi_module modules/mod_wsgi.so\n")
            if not port:
                httpd_config.append("Listen {}\n".format(port_num))
        fh.writelines(httpd_config)
    # write over the /etc/environment file with the new lines from the tmp file
    check_call(['sudo', 'cp', '/tmp/httpd_conf', httpd_path])
    # remove the temporary file that was created
    check_call(['sudo', 'rm', '-f', '/tmp/httpd_conf'])

    print TF.format("Apache's httpd.conf was configured successfully!\n", 1)


if __name__ == '__main__':
    # create an instance of our Terminal Fonts class to help with printing
    TF = TerminalFonts()

    # ask for the full path to the OnRamp server directory since we're gonna need it later
    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp server directory: ")
    onramp_dir = validate_path(onramp_dir, remove_slash=True)

    apache_dir = raw_input("\nPlease enter in the full path to your apache 2.4 directory: ")
    apache_dir = validate_path(apache_dir, remove_slash=True)

    # ask for the full path to the apache 2.2 modules directory because we have to install mod_wsgi there
    modules_dir = raw_input("Please enter in the full path to your apache modules directory: ")
    modules_dir = validate_path(modules_dir, filename='httpd.conf', remove_slash=True)

    # ask for the port to run the OnRamp webserver under
    port = raw_input("\nPlease enter in the port you wish to run OnRamp under: ")
    while not port.isdigit():
        port = raw_input("Please enter in a valid port to run OnRamp under: ")

    print  # Just printing a blank line here for space

    # add the required vhost directive to the apache httpd-vhost config
    configure_vhost_conf(TF, onramp_dir, apache_dir, port)
    configure_httpd_conf(TF, apache_dir, port)
    install_wsgi(TF, modules_dir)

    print TF.format("\nPlease restart your apache to complete the configuration.\n", 1)
