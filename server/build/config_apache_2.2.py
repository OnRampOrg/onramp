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


def configure_apache(TF, onramp_dir, mod_dir, port_num):
    print "Preparing to configure apache...\n"

    # strip off any trailing slashes so we have clean paths in the config
    if onramp_dir.endswith("/"):
        onramp_dir = onramp_dir[:-1]

    # get the full path to the httpd.conf file so we can append our OnRamp configuration
    httpd_path = raw_input("Please enter in the full path to your httpd.conf: ")
    httpd_path = validate_path(httpd_path, filename=None)  # leaving filename as none because it could be anything

    # read in the current httpd.conf lines so we can append our OnRamp configuration
    httpd_config = []
    fh = open(httpd_path, "r")
    for line in fh.readlines():
        httpd_config.append(line)
        if "CUSTOM SETTINGS FOR ONRAMP" in line:
            print "%s: The httpd.conf file already contains custom setting for OnRamp!" % TF.format("ERROR", 4)
            print "Please remove the custom settings for OnRamp if you would like to\n" \
                  "re-configure your Apache 2.2 webserver for OnRamp.\n" % port_num
            sys.exit(1)
    fh.close()

    # custom setting for Django and the OnRamp webserver
    onramp_config = """

    # CUSTOM SETTINGS FOR ONRAMP

    LoadModule wsgi_module {mod_dir}/mod_wsgi.so

    WSGIScriptAlias / {onramp_dir}/ui/wsgi.py
    WSGIPythonPath {onramp_dir}:{onramp_dir}/virtual-env/lib/python2.7/site-packages
    Alias /static {onramp_dir}/ui/static

    Listen {port}

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
    </VirtualHost>
    """.format(onramp_dir=onramp_dir, mod_dir=mod_dir, port=port)

    # write out the new lines to a temp file to copy over with sudo
    with open("/tmp/httpd_conf", "w") as fh:
        httpd_config += "".join(textwrap.dedent(onramp_config))
        fh.writelines(httpd_config)
    # write over the /etc/environment file with the new lines from the tmp file
    check_call(['sudo', 'cp', '/tmp/httpd_conf', httpd_path])
    # remove the temporary file that was created
    check_call(['sudo', 'rm', '-f', '/tmp/httpd_conf'])

    print TF.format("Apache was configured successfully!\n", 1)


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
    check_call(['tar', '-zxpvf', wsgi_tar_src])

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


if __name__ == '__main__':
    # create an instance of our Terminal Fonts class to help with printing
    TF = TerminalFonts()

    # ask for the full path to the OnRamp server directory since we're gonna need it later
    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp server directory: ")
    onramp_dir = validate_path(onramp_dir, remove_slash=True)

    # ask for the full path to the apache 2.2 modules directory because we have to install mod_wsgi there
    modules_dir = raw_input("Please enter in the full path to your apache modules directory: ")
    modules_dir = validate_path(modules_dir, filename='httpd.conf', remove_slash=True)

    # ask for the port to run the OnRamp webserver under
    port = raw_input("\nPlease enter in the port you wish to run OnRamp under: ")
    while not port.isdigit():
        port = raw_input("Please enter in a valid port to run OnRamp under: ")

    # add the special settings we need for OnRamp to the httpd.conf file
    configure_apache(TF, onramp_dir, modules_dir, port)
    # build mod wsgi from source since we need it run django
    install_wsgi(TF, modules_dir)

    print TF.format("\nPlease restart your apache to complete the configuration.\n", 1)
