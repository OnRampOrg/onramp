
import site
import sys
import os

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('../virtual-env')

# Add the app's directory to the PYTHONPATH
sys.path.append("../")
sys.path.append('../ui')
sys.path.append("../virtual-env/lib/python2.7/site-packages")

# to set environment settings for Django apps
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")

from utils.terminal import TerminalFonts
from argparse import ArgumentParser
from subprocess import *
from time import sleep
import traceback
import textwrap
import shutil


def catch_exceptions(func):
    def run(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            error = TerminalFonts().format("Installation Error", 4)
            print "\n{}[ {} ]{}".format("=" * 25, error, "=" * 25)
            print traceback.format_exc().strip()
            print "{}\n".format("=" * 72)
            os._exit(-1)
    return run


class Installer(object):

    def __init__(self, args):
        self.reinstall = args.reinstall
        self.verbose = args.v
        self.devnull = open(os.devnull, 'w')
        self.build_dir = os.getcwd()
        self.base_dir = "/".join(os.getcwd().split("/")[0:-1])
        self.dep_dir = "{}/dependencies".format(self.build_dir)
        self.apachectl = "{}/webserver/bin/apachectl".format(self.base_dir)
        self.phases = [
            {'phase': 0, 'func': self.configure_environment, 'desc': '(0): Configure Environment'},
            {'phase': 1, 'func': self.install_dependencies, 'desc': '(1): Install Dependencies'},
            # NOTE: install_mysql must run before install_virtual_env because the python mysqlclient
            # library apparently requires mysql to already be installed before it can install properly
            {'phase': 2, 'func': self.install_mysql, 'desc': '(2): Install MySQL'},
            {'phase': 3, 'func': self.install_virtual_env, 'desc': '(3): Install Virtual Environment'},
            {'phase': 4, 'func': self.install_apache, 'desc': '(4): Install Apache'},
            {'phase': 5, 'func': self.install_wsgi, 'desc': '(5): Install WSGI'},
            {'phase': 6, 'func': self.run_migrations, 'desc': '(6): Run Django Migrations'},
            {'phase': 7, 'func': self.create_admin_user, 'desc': '(7): Create Admin User'},
        ]
        self.TF = TerminalFonts()

    def print_phases(self):
        print
        for phase in self.phases:
            print phase['desc']
        print

    @catch_exceptions
    def subproc(self, command, **kwargs):
        if kwargs.pop('ignore', False):
            call(command, stdout=self.devnull, stderr=self.devnull, **kwargs)
        elif not self.verbose:
            check_call(command, stdout=self.devnull, stderr=self.devnull, **kwargs)
        else:
            print check_output(command, **kwargs)

    @catch_exceptions
    def rm(self, path, force=False):
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    self.subproc(['sudo', 'rm', '-f', path])
                if os.path.isdir(path):
                    # IMPORTANT: this is VERY dangerous if used on the wrong path
                    self.subproc(['sudo', 'rm', '-rf', path])
                print "Removed: {}\n".format(path)
                sleep(1)
            except:
                if not force: raise
        else:
            if not force:
                raise OSError("{} does not exists!".format(path))

    @catch_exceptions
    def configure_environment(self):
        print "Preparing to configure environment...\n"

        # read in the existing environment variables from /etc/environment
        fh = open("/etc/environment", "r")
        lines = fh.readlines()
        fh.close()

        # just defining envrionment variables that need to get put on the path
        django_settings_module = "DJANGO_SETTINGS_MODULE='ui.settings'"
        python_path = "PYTHONPATH='{base}/virtual-env/lib/python2.7/" \
                      "site-packages:{base}'".format(base=self.base_dir)

        # add the required lines to the existing /etc/environment file
        if django_settings_module not in lines:
            lines.append("{}\n".format(django_settings_module))
        if python_path not in lines:
            lines.append("{}\n".format(python_path))

        # write out the new lines to a temp file to copy over with sudo
        with open("/tmp/etc_environment", "w") as fh:
            fh.writelines(lines)
        # write over the /etc/environment file with the new lines from the tmp file
        self.subproc(['sudo', 'cp', '/tmp/etc_environment', '/etc/environment'])
        # remove the temporary file that was created
        self.rm('/tmp/etc_environment', force=True)

        print self.TF.format("Environment configured successfully!\n", 1)

    @catch_exceptions
    def install_dependencies(self):
        print "Preparing to install dependencies...\n"

        dependencies = [
            'apr-util-devel',
            'openssl-devel',
            'python-devel',
            'python-pip',
            'pcre-devel',
            'zlib-devel',
            'apr-devel',
        ]
        if self.reinstall:
            for dep in dependencies:
                self.subproc(['sudo', 'yum', 'remove', '-y', dep])

        for dep in dependencies:
            self.subproc(['sudo', 'yum', 'install', '-y', dep])

        print self.TF.format("Dependencies installed successfully!\n", 1)

    @catch_exceptions
    def install_mysql(self):
        print "Preparing to install MySQL...\n"

        mysql_dir = '{}/mysql'.format(self.base_dir)

        if self.reinstall:
            self.subproc(['sudo', 'systemctl', 'stop', 'mysqld.service'], ignore=True)
            self.subproc(['sudo', 'systemctl', 'disable', 'mysqld.service'], ignore=True)
            self.subproc(['sudo', 'yum', 'remove', '-y', 'mysql-community-server'], ignore=True)
            self.subproc(['sudo', 'yum', 'remove', '-y', 'mysql-community-devel'], ignore=True)
            self.rm('/var/log/mysqld.log', force=True)
            self.rm('/var/lib/mysql', force=True)
            self.rm('/etc/my.cnf', force=True)
            self.rm(mysql_dir, force=True)

        # TODO: check version of centos here for install
        # self.subproc(['sudo', 'yum', 'localinstall', '-y', '{}/mysql57-community-release-el6-7.noarch.rpm'.format(self.dep_dir)])

        print "Installing mysql-community-server..."
        self.subproc(['sudo', 'yum', 'localinstall', '-y', '{}/MySQL-server-5.5.53-1.el6.x86_64.rpm'.format(self.dep_dir)])

        print "Installing mysql-community-devel..."
        self.subproc(['sudo', 'yum', 'localinstall', '-y', '{}/MySQL-devel-5.5.53-1.el6.x86_64.rpm'.format(self.dep_dir)])

        print "Stopping any running MySQL services..."
        self.subproc(['sudo', 'systemctl', 'stop', 'mysqld.service'], ignore=True)

        print "Initializing MySQL data directory..."
        self.subproc(['sudo', 'mysqld', '--initialize', '--user=mysql', '--datadir={}'.format(mysql_dir)])

        print "Removing the default MySQL data directory..."
        self.rm("/var/lib/mysql")

        print "Copying over MySQL configuration file...\n"
        fh = open("{}/build/config/my.cnf".format(self.base_dir), 'r')
        mysql_conf = fh.read().strip()
        fh.close()
        # write out the new lines to a temp file to copy over with sudo
        with open("/tmp/mysql_conf", "w") as fh:
            fh.writelines(mysql_conf.replace("ONRAMP", self.base_dir))
        # write over the /etc/environment file with the new lines from the tmp file
        self.subproc(['sudo', 'cp', '/tmp/mysql_conf', '/etc/my.cnf'])
        # remove the temporary file that was created
        self.rm('/tmp/mysql_conf', force=True)

        print "Fixing SELinux for new MySQL data directory..."
        self.subproc(['sudo', 'semanage', 'fcontext', '-a', '-s', 'system_u',
                      '-t', 'mysqld_db_t', '"{}(/.*)?"'.format(mysql_dir)])
        self.subproc(['sudo', 'restorecon', '-Rv', mysql_dir])

        print "Starting MySQL service..."
        self.subproc(['sudo', 'systemctl', 'start', 'mysqld.service'])

        # have to get the password this way because can't get it in python without root privileges
        p = Popen(['sudo grep "temporary password" /var/log/mysqld.log'],
                  shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        password = stdout.split("localhost: ")[1].strip()

        # authenticate with the default temporary root password from the mysql log
        auth = ['sudo', 'mysql', '-u', 'root', '--password={}'.format(password), '--connect-expired-password']

        print "Changing the root password for MySQL..."
        # change the password for the root user from the default temporary password in the log
        self.subproc(auth + ['-e', "ALTER USER 'root'@'localhost' IDENTIFIED BY '0nR@mp!'"])

        # authenticate with the new super user password for root
        auth = ['sudo', 'mysql', '-u', 'root', '--password=0nR@mp!']

        print "Removing default users and directories for MySQL..."
        # make sure to remove the default users and default databases
        self.subproc(auth + ['-e', "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"])
        self.subproc(auth + ['-e', "DELETE FROM mysql.user WHERE User=''"])
        self.subproc(auth + ['-e', "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"])
        print "Creating MySQL user for django..."
        # creating onramp user for django to authenticate with
        self.subproc(auth + ['-e', "CREATE USER 'onramp'@'localhost' IDENTIFIED BY 'OnRamp_16'"])
        self.subproc(auth + ['-e', "GRANT ALL PRIVILEGES ON * . * TO 'onramp'@'localhost'"])
        print "Creating MySQL database for django..."
        # creating the default database for django to use
        self.subproc(auth + ['-e', "CREATE DATABASE django"])
        print "Reloading all permissions for MySQL..."
        # reload all privileges so that the new user can log in
        self.subproc(auth + ['-e', "FLUSH PRIVILEGES"])

        print self.TF.format("MySQL installed successfully!\n", 1)

    @catch_exceptions
    def install_virtual_env(self):
        print "Preparing to install virtual environment..."

        if self.reinstall:
            self.rm("../virtual-env", force=True)

        if not self.reinstall and os.path.exists("../virtual-env"):
            answer = raw_input("\nThe virtual environment has already been installed. "
                                    "\nWould you like to reinstall it? (y/[N]):  ")
            if answer != 'y' and answer != 'Y':
                return
            else:
                self.rm("../virtual-env", force=True)

        print "Upgrading pip to the latest version..."
        self.subproc(['sudo', 'pip', 'install', '--upgrade', 'pip'])

        print "Installing virtualenv..."
        self.subproc(['sudo', 'pip', 'install', 'virtualenv'])

        print "Building virtual environment directory without site packages..."
        self.subproc(['virtualenv', '-p', sys.executable, '../virtual-env'])

        # IMPORTANT: we need to do the following to make sure we are actually
        # installing our python packages in the correct virtual environment
        activate_this_file = "../virtual-env/bin/activate_this.py"
        execfile(activate_this_file, dict(__file__=activate_this_file))

        print "Activating virtual environment and installing dependencies...."
        pip_dependencies = [
            'mysqlclient',
            'requests',
            'django',
        ]
        for dependency in pip_dependencies:
            self.subproc(['pip', 'install', dependency])

        print self.TF.format("Virtual environment installed successfully!\n", 1)

    @catch_exceptions
    def install_apache(self):
        print "Preparing to install apache...\n"

        if self.reinstall:
            if os.path.exists(self.apachectl):
                print "Stopping the running apache at {}/webserver\n".format(self.base_dir)
                self.subproc(['sudo', self.apachectl, 'stop'], ignore=True)
            self.rm("{}/httpd-2.4.23".format(self.dep_dir), force=True)
            self.rm("{}/webserver/".format(self.base_dir), force=True)

        if not self.reinstall and os.path.exists("{}/webserver".format(self.base_dir)):
            answer = raw_input("Apache has already been installed. "
                       "\nWould you like to reinstall it? (y/[N]):  ")
            if answer != 'y' and answer != 'Y':
                return
            else:
                self.rm("{}/httpd-2.4.23".format(self.dep_dir), force=True)
                self.rm("{}/webserver/".format(self.base_dir), force=True)

        print "Creating webserver directory...\n"
        os.makedirs("{}/webserver".format(self.base_dir))

        apache_tar_src = "{}/httpd-2.4.23.tar.gz".format(self.dep_dir)
        apache_src = "{}/httpd-2.4.23".format(self.dep_dir)

        os.chdir(self.dep_dir)

        print "Un-tarring apache source...\n"
        self.subproc(['tar', '-zxpvf', apache_tar_src])

        os.chdir(apache_src)

        config = """
            sudo ./configure
            --prefix={base_dir}/webserver
            --enable-nonportable-atomics=yes
            --with-mpm=worker
            --enable-core=static
            --enable-unixd=static
            --enable-ssl=static
            --enable-socache_shmcb=static
            --enable-authz_core=static
            --enable-allowmethods=static
            --enable-headers=static
            --enable-expires=static
            --enable-alias=static
            --enable-rewrite=static
            --enable-filter=static
            --enable-deflate=static
            --enable-cache=static
            --enable-log_config=static
            --enable-mime=static
            --enable-env=static
            --disable-authn_core
            --disable-authn_file
            --disable-authz_host
            --disable-authz_groupfile
            --disable-authz_user
            --disable-access_compat
            --disable-mime_magic
            --disable-auth_basic
            --disable-setenvif
            --disable-version
            --disable-autoindex
            --disable-dir
        """.format(base_dir=self.base_dir)

        print "Running apache configure...\n"
        self.subproc(config.strip().split())

        print "Building apache...\n"
        self.subproc(['sudo', 'make'])

        print "Installing apache...\n"
        self.subproc(['sudo', 'make', 'install'])

        print "Cleaning up apache source...\n"
        self.rm(apache_src)

        print "Removing default virtual hosts...\n"
        vhost_path = "{}/webserver/conf/extra/httpd-vhosts.conf".format(self.base_dir)
        fh = open(vhost_path, 'r')
        lines = []
        for line in fh.readlines():
            if line.startswith("#"):
                lines.append(line)
        # write out the new lines to a temp file to copy over with sudo
        with open("/tmp/httpd_vhost_conf", "w") as fh:
            fh.writelines(lines)
        # write over the /etc/environment file with the new lines from the tmp file
        self.subproc(['sudo', 'cp', '/tmp/httpd_vhost_conf', vhost_path])
        # remove the temporary file that was created
        self.rm('/tmp/mysql_conf', force=True)

        print "Copying over httpd.conf...\n"
        fh = open("{}/build/config/httpd.conf".format(self.base_dir), 'r')
        httpd_conf = fh.read().strip()
        fh.close()
        # write out the new lines to a temp file to copy over with sudo
        with open("/tmp/httpd_conf", "w") as fh:
            fh.writelines(httpd_conf.replace("ONRAMP", "{}/webserver".format(self.base_dir)))
        # write over the /etc/environment file with the new lines from the tmp file
        self.subproc(['sudo', 'cp', '/tmp/httpd_conf',
            "{}/webserver/conf/httpd.conf".format(self.base_dir)])
        # remove the temporary file that was created
        self.rm('/tmp/httpd_conf', force=True)

        print "Configuring httpd-vhosts.conf..."
        fh = open("{}/build/config/httpd-vhosts.conf".format(self.base_dir), 'r')
        httpd_vhost = fh.read().strip()
        fh.close()
        # write out the new lines to a temp file to copy over with sudo
        with open("/tmp/httpd_vhosts", "w") as fh:
            fh.writelines(httpd_vhost.replace("ONRAMP", self.base_dir))
        # write over the /etc/environment file with the new lines from the tmp file
        self.subproc(['sudo', 'cp', '/tmp/httpd_vhosts',
                      "{}/webserver/conf/extra/httpd-vhosts.conf".format(self.base_dir)])
        # remove the temporary file that was created
        self.rm('/tmp/httpd_vhosts', force=True)

        print self.TF.format("Apache installed successfully!\n", 1)

    @catch_exceptions
    def install_wsgi(self):
        print "Preparing to install mod wsgi...\n"

        if self.reinstall:
            self.rm("{}/webserver/modules/mod_wsgi.so".format(self.base_dir), force=True)
            self.rm("{}/mod_wsgi-4.5.7".format(self.dep_dir), force=True)

        wsgi_so = "{}/webserver/modules/mod_wsgi.so".format(self.base_dir)
        if not self.reinstall and os.path.exists(wsgi_so):
            answer = raw_input("Mod wsgi has already been installed. "
                       "\nWould you like to reinstall it? (y/[N]):  ")
            if answer != 'y' and answer != 'Y':
                return
            else:
                self.rm("{}/webserver/modules/mod_wsgi.so".format(self.base_dir), force=True)
                self.rm("{}/mod_wsgi-4.5.7".format(self.dep_dir), force=True)

        wsgi_tar_src = '{}/mod_wsgi-4.5.7.tar.gz'.format(self.dep_dir)
        wsgi_src = '{}/mod_wsgi-4.5.7'.format(self.dep_dir)

        os.chdir(self.dep_dir)

        print "Un-tarring mod wsgi 4.5.7 source...\n"
        self.subproc(['tar', '-zxpvf', wsgi_tar_src])

        os.chdir(wsgi_src)

        config = """
        sudo ./configure --with-apxs={base_dir}/webserver/bin/apxs
            --with-python={base_dir}/virtual-env/bin/python
        """.format(base_dir=self.base_dir)

        print "Running mod wsgi configure...\n"
        self.subproc(config.strip().split())

        print "Building mod wsgi...\n"
        self.subproc(['sudo', 'make'])

        print "Installing mod wsgi...\n"
        self.subproc(['sudo', 'make', 'install'])

        print "Cleaning up mod wsgi source...\n"
        self.rm(wsgi_src)

        print self.TF.format("Mod wsgi installed successfully!\n", 1)

        print "Starting up apache...\n"
        self.subproc(['sudo', self.apachectl, "start"])

    @catch_exceptions
    def run_migrations(self):
        import _mysql

        print "Running django migrations"

        if self.reinstall:
            # remove all of the migration files from the public and admin django apps
            public = '{}/ui/public/migrations/'.format(self.base_dir)
            for file in os.listdir(public):
                path = os.path.join(public, file)
                if '__init__' not in path:
                    os.remove(path)
            admin = '{}/ui/admin/migrations/'.format(self.base_dir)
            for file in os.listdir(admin):
                path = os.path.join(admin, file)
                if '__init__' not in path:
                    os.remove(path)
            conn = _mysql.connect(host='127.0.0.1', user='onramp',
                                  passwd='OnRamp_16', db='django')
            try:
                conn.query('TRUNCATE django_migrations')
            except _mysql.ProgrammingError:
                pass  # just ignore the error if the table doesn't exists
            try:
                conn.query('DROP DATABASE django')
            except _mysql.ProgrammingError:
                pass  # just ignore the error if the database doesn't exists
            conn.query('CREATE DATABASE django')
            conn.commit()
            conn.close()

        # make sure to change to the ui directory before calling migrate
        os.chdir("{}/ui".format(self.base_dir))

        # call migrate using the manage.py utility from django to build
        # migrations and create the necessary tables in the MySQL database
        self.subproc([sys.executable, '{}/ui/manage.py'.format(self.base_dir), 'migrate'])

        print self.TF.format("Migrations built successfully.", 1)

    @catch_exceptions
    def create_admin_user(self):
        # have to setup django before we attempt to import a model
        import django
        django.setup()

        from django.contrib.auth.models import User
        from django.db import IntegrityError

        print "Creating the django admin user..."
        if self.reinstall:
            # TODO: figure out why this doesn't work
            try:
                User.objects.get(username='admin').delete()
            except User.DoesNotExist:
                pass
        try:
            User.objects.create_superuser("admin", "", "admin123")
            print self.TF.format("Admin user created!\n  username: admin\n  password: admin123", 1)
        except IntegrityError:
            print "{}: An admin user with same username \"admin\" " \
                "already exists.".format(self.TF.format("ERROR", 4))

    def run(self):
        print "\nSTARTING INSTALLATION\n"
        # make sure this script is ran with nothing less than python 2.7
        assert (not sys.version_info < (2, 7))
        # loop over all of the phases in the install process and run them
        for phase in self.phases:
            phase['func']()
            sleep(2)
        print "Please logout then back in to complete the OnRamp installation process!"
        sleep(3)
        self.TF.format("INSTALLATION COMPLETE\n", 1)

if __name__ == '__main__':
    parser = ArgumentParser("Tool to build and install OnRamp webserver and interface.")
    parser.add_argument("-p", nargs=1, type=int, help='The phase of the install to run')
    parser.add_argument("-l", action="store_true", help='Prints the phases of the install')
    parser.add_argument("-r", "--reinstall", action="store_true", help="Flag for reinstall")
    parser.add_argument("-v", action="store_true", help="Flag for verbose output")
    args = parser.parse_args()

    if args.l:
        Installer(args).print_phases()
        sys.exit(0)
    elif args.p:
        if args.p[0] == 0:
            print "\nConfiguring the environment requires logging out\n" \
                  "then back in again for the changes to take effect.\n"
        try:
            installer = Installer(args)
            installer.phases[args.p[0]]['func']()
        except:
            print "Please select a valid phase of the install to run."
            sys.exit(0)
    else:
        Installer(args).run()
