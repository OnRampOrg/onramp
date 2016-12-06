from utils.terminal import TerminalFonts
from subprocess import *
import textwrap
import shutil
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


def configure_apache(TF, onramp_dir, apache_dir, port_num):
    print "Preparing to configure apache...\n"

    # strip off any trailing slashes so we have clean paths in the config
    if onramp_dir.endswith("/"): onramp_dir = onramp_dir[:-1]

    # strip off any trailing slashes so we have clean paths in the config
    if apache_dir.endswith("/"): apache_dir = apache_dir[:-1]

    # NOTE: the default apache 2.2 virtual hosts file should be the following
    vhosts = raw_input("Please enter in the full path to your virtual host file: ")
    vhosts = validate_path(vhosts, filename=None)  # leaving filename as none because it could be anything

    fh = open(vhosts, "r")
    for line in fh.readlines():
        if ":%s" % port_num in line:
            print "%s: The virtual hosts file already contains an entry for that port!" % TF.format("ERROR", 4)
            print "If you would like to run OnRamp under the port (%s) please remove the\n" \
                  "current configuration for that port from your enabled virtual hosts file\n" \
                  "and then re-run this script to configure your Apache 2.2 webserver for OnRamp.\n" % port_num
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

    print "Apache's virtual hosts file was configured successfully!\n"

    print "Configuring apache's ports.conf file..."
    ports_conf = raw_input("Please enter in the full path to your ports.conf file: ")
    ports_conf = validate_path(ports_conf, filename="ports.conf")
    with open(ports_conf, "a+") as fh:
        if port_num not in fh.read():
            fh.write("# CUSTOM SETTINGS FOR ONRAMP\n")
            fh.write("Listen %s" % port_num)
            fh.close()
            print "Apache's ports.conf file configured successfully!\n"
        else:
            print 'Apache is already configured to listen on that port!\n'

    print TF.format("Apache's was configured successfully!\n", 1)


def install_wsgi(TF, apache_dir):
    print "Preparing to install Mod WSGI...\n"

    # removing the mod wsgi source if it exists already
    if os.path.exists("./dependencies/mod_wsgi-4.5.7"):
        shutil.rmtree("./dependencies/mod_wsgi-4.5.7")

    modules_dir = raw_input("Please enter in the full path to your apache modules directory: ")
    modules_dir = validate_path(modules_dir, filename=None, remove_slash=True)

    wsgi_so = "%s/mod_wsgi.so" % modules_dir
    if os.path.exists(wsgi_so):
        answer = raw_input("Mod WSGI has already been installed. "
                    "\nWould you like to reinstall it? (y/[N]):  ")
        if answer in ['y', 'Y']:
            try:
                os.remove(wsgi_so)
                shutil.rmtree("./dependencies/mod_wsgi-4.5.7")
            except:
                pass
        else:
            return

    os.chdir('./dependencies')

    wsgi_tar_src = './mod_wsgi-4.5.7.tar.gz'
    wsgi_src = './mod_wsgi-4.5.7'

    print "Un-tarring mod wsgi 4.5.7 source...\n"
    check_call(['tar', '-zxpvf', wsgi_tar_src])

    os.chdir(wsgi_src)

    print "Running mod wsgi configure...\n"
    # apparently the configure script will find the apxs
    # executable automatically if it is installed in its
    # standard location
    check_call("./configure --with-python=%s" % sys.executable)

    print "Building mod wsgi...\n"
    check_call(['make'])

    print "Installing mod wsgi...\n"
    check_call(['make', 'install'])

    print "Cleaning up mod wsgi source...\n"
    shutil.rmtree('../mod_wsgi-4.5.7')

    mods_enabled_dir = raw_input("Please enter in the full path to your mods-enabled directory: ")
    mods_enabled_dir = validate_path(mods_enabled_dir, filename=None, remove_slash=True)

    # mods_enabled = os.listdir(mods_enabled_dir)
    # if "wsgi" not in "".join(mods_enabled):
    #     # create the required conf file for wsgi
    #     fh = open("{}/wsgi.conf", 'w')
    #     fh.write("LoadModule wsgi_module %s/mod_wsgi.so" % modules_dir)
    #     fh.close()
    #     # create the required load file for wsgi
    #     # NOTE: no need to add anything to this
    #     # because all of our settings are in the
    #     # virtual hosts file
    #     open("{}/wsgi.conf", 'w').close()

    print TF.format("Mod WSGI installed successfully!\n", 1)


if __name__ == '__main__':
    # create an instance of our Terminal Fonts class to help with printing
    TF = TerminalFonts()

    # check to make sure we have root permissions to execute the script
    # since we need those permissions to install dependencies through yum
    if os.getuid() != 0:
        print '\n%s: Please run this script with "sudo" or as the ' \
              'root user.\n' % TF.format("Permission Error", 4)
        sys.exit(0)

    onramp_dir = raw_input("\nPlease enter in the full path to the OnRamp server directory: ")
    if not onramp_dir.startswith("/") and not os.path.isdir(onramp_dir):
        print "Please enter in a valid directory path!"
        sys.exit(1)

    apache_dir = raw_input("\nPlease enter in the full path to your apache 2.2 directory: ")
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
    configure_apache(TF, onramp_dir, apache_dir, port)
    install_wsgi(TF, apache_dir)

    print TF.format("\nPlease restart your apache to complete the configuration.\n", 1)
