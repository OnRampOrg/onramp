## OnRamp Build Instructions

##### Summary
The following instructions in this file are to document the installation of the **OnRamp** server. The server is the web application that the users of OnRamp will interact directly with and consists of the following dependencies: 
- [Python 2.7](https://docs.python.org/2/)
- [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
- [Apache 2.4.23](https://httpd.apache.org/docs/2.4/)
- [Mod WSGI 4.5.7](https://modwsgi.readthedocs.io/en/develop/)
- [Django 1.10](https://docs.djangoproject.com/en/1.10/) 
- [MySQL 5.7](http://dev.mysql.com/doc/refman/5.7/en/)  

The installation of the server occurs in the `install.py` file found in the `/path/to/onramp/server/build/` directory. The purpose of these instructions is to explain each individual step of the install process and what it is doing, in addition to providing adequate instructions for an individual to install the server manually should the install script not suffice. If the `install.py` file is not run to install OnRamp and it is manually installed via the instructions in this file, then **ALL** steps in this file must be run for a complete and working server.

##### Notes:
- This file documents everything that happens in the `install.py` file
- Most of the commands in this document should be run with sudo privileges

##### Important:
- Everywhere in this document where you see **ONRAMP** repace it with `/path/to/your/onramp/directory/`

---

### 1. Python Virtual Environment
This step is **VERY** important. A virtual environment is necessary for the OnRamp server because it will prevent the dependencies of the OnRamp server from clashing with the system wide dependencies of the machine. By creating a virtual environment for OnRamp we also make sure none of the system dependencies interfere with OnRamp which could potentially break imports in the python code due to different versions. This step needs to be run before any of the following steps due to the fact the rest of the instructions rely on python and the following dependencies to be there. 

- **Note:** For further documentation on python virtual environments and what the following commands do please read the link in the summary section of this documentation

##### How to setup virtual environment

- First, upgrade pip to make sure it's at the latest version (it will complain otherwise)
    ```
    user@server:/# pip install --upgrade pip 
    ```

- Install the virtualenv module so we can create virtual environments
    ```
    user@server:/# pip install virtualenv
    ```

- Create a new virtual environment in the OnRamp directory with python2.7
    ```
    user@server:/# virtualenv -p /usr/bin/python2.7 ONRAMP/server/virtual-env'
    ```

- Activate the virtual environment so we can install dependencies into it
    ```
    user@server:/# source ONRAMP/server/virtual-env/bin/activate 
    ```

- Install the required dependencies into the virtual environment
    ```
    (virtual-env) [user@server:/#] pip install mysqlclient 
    (virtual-env) [user@server:/#] pip install django 
    ```

- Deactivate the virtual environment once the dependencies are installed
    ```
    (virtual-env) [user@server:/#] deactivate
    ```
    
- The virtual environment should be successfully installed and working

---

### 2. Apache 2.4.23 Setup
Apache is the main component of the OnRamp server. It is the web server that Django runs under via Mod WSGI. Without Apache, there would be no OnRamp and no web interface for users to communicate to the server with. The following instructions document the installation of the Apache server from source in addition to the required dependencies to do so. Apache doesn't necessarily have to be built this way however building it from source will give you more control over what modules are built statically versus dynamically in addition to controlling where apache is installed. If you choose not to install apache this way it can be installed via your default OS package management tool via apt-get, yum, rpm, etc. However, the **recommended** way to install Apache for the OnRamp server is documented below.

- **Note:** For further documentation on Apache and what the following commands do please read the link in the summary section of this documentation

##### Centos 7 Dependencies
The following dependencies need to be installed before attempting to install Apache from source because if they are not present during the installation process the following commands after this step will fail.

- Install the following required dependencies through yum 
    ```
    user@server:/# yum install -y apr-devel
    user@server:/# yum install -y apr-util-devel
    user@server:/# yum install -y pcre-devel
    user@server:/# yum install -y zlib-devel
    user@server:/# yum install -y openssl-devel
    ```

##### How to install apache from source
The source for Apache 2.4.23 has already been conveniently downloaded and is available in the dependencies folder of the onramp server build directory. The version 2.4.23 isn't a strict requirement and any new version of Apache could probably be built the same way if needed. The following instructions cover un-tarring Apache's source, configuring it with some default modules loaded statically and other modules disabled for performance reasons, and the installation of it into the OnRamp server directory for convenience.

- Un-tar the Apache 2.4.23 source with the following commands
    ```
    user@server:/# cd ONRAMP/server/build/dependencies/
    user@server:/# tar -zxpvf httpd-2.4.23.tar.gz
    ```
    
- Run the following command below to configure Apache for installation:
    - **Note:** The following command may look quite intimidating howerver everything below is setup to optomize apache and make sure no unecessary modules are loaded into apache that aren't needed to maximize performance. All of the additional arguments below can be looked up via the link in the summary to the Apache 2.4 documentation or by typing `./configure --help | less ` in the terminal and scrolling through the output.
    ```
    user@server:/# ./configure --prefix=/Aristotle/apache2 --enable-nonportable-atomics=yes --enable-core=static --enable-unixd=static --enable-ssl=static --enable-socache_shmcb=static --enable-authz_core=static --enable-allowmethods=static --enable-headers=static --enable-expires=static --enable-alias=static --enable-rewrite=static --enable-filter=static --enable-deflate=static --enable-cache=static --enable-log_config=static --enable-mime=static --enable-env=static --enable-proxy=static --enable-proxy-wstunnel=static --disable-authn_core --disable-authn_file --disable-authz_host --disable-authz_groupfile --disable-authz_user --disable-access_compat --disable-mime_magic --disable-auth_basic --disable-setenvif --disable-version --disable-autoindex --disable-dir --disable-proxy-balancer --disable-proxy-connect --disable-proxy-ftp --disable-proxy-http --disable-proxy-fcgi --disable-proxy-scgi --disable-proxy-ajp --disable-proxy-express --disable-lbmethod_byrequests --disable-lbmethod_bytraffic --disable-lbmethod_bybusyness --disable-lbmethod_heartbeat
    ```
    
- Build Apache from source via the following command
    ```
    user@server:/# make
    ```
    
- Install Apache into the correct location via the following command
    ```
    user@server:/# make install
    ```

- Apache should now be installed at `ONRAMP/server/webserver`
- Copy over `ONRAMP/server/build/config/httpd.conf` to the default Apache location via the following command
    - **Note:** The following command makes sure Apache is setup correctly for OnRamp since `httpd.conf` is the main file that apache reads to determine what its settings are, in addition to the `httpd-vhost.conf` file which tells apache what to server up for what IP/port combination. The httpd.conf file in the `ONRAMP/server/build/config` directory has already been configured for OnRamp so nothing has to change besides some paths. 
    ```
    user@server:/# cp ONRAMP/server/build/config/httpd.conf ONRAMP/server/webserver/conf/httpd.conf
    ```
    
- Replace every instance of `ONRAMP` in the `httpd.conf` file with `ONRAMP/server/webserver`
- Copy over `ONRAMP/server/build/config/httpd-vhosts.conf` to the default Apache location via the following command
    - **Note:** The following command makes sure Apache is listening on the correct IP and port for OnRamp in addition to making sure Apache is setup properly to use the WSGI module that is installed later on in the instructions. Without this file setup properly Apache would run but no user would be able to get to the web application to do anything.
    ```
    user@server:/# cp ONRAMP/server/build/config/httpd-vhosts.conf ONRAMP/server/webserver/conf/extra/httpd-vhosts.conf
    ```
    
- Replace every instance of `ONRAMP` in the `httpd-vhosts.conf` file with `ONRAMP/server/webserver`
- Apache should be successfully installed and be running

---

### 3. Mod WSGI Setup
Mod WSGI is the main component that allows the Django framework to run under Apache and actually serve up content to OnRamp users through Apache. Mod WSGI is an apache module that allows python to run in the child processes of Apache. Without Mod WSGI OnRamp users could connect to the OnRamp server due to Apache but no content would be served. Mod WSGI is required for the setup of the OnRamp server. Once again this is not the only way to install Mod WSGI, however, this is the **recommended** way to install it for OnRamp. Mod WSGI can be installed through a package management tool however typically the version available is usually not up to date. Also the version `4.5.7` is not a script requirement. Any version of Mod WSGI should suffice and if a new version is available that may be preferred.

- **Important:** The steps below require Apache and the Python Virtual Environment to be installed 
- **Note:** For further documentation on Mod WSGI and what the following commands do please read the link in the summary section of this documentation


##### How to install Mod WSGI from source
- Install the python development libraries via the following command
    - **Note:** The python-devel dependency is required to install Mod WSGI from source
    ```
    user@server:/# yum install python-devel
    ```
    
- Un-tar the Mod WSGI 4.5.7 source via the following command 
    ```
    user@server:/# cd ONRAMP/server/build/dependencies
    user@server:/# tar -zxpvf mod_wsgi-4.5.7.tar.gz
    ```
    
- Configure Mod WSGI with the following command
    - **Note:** The following command makes sure the module is installed into the correct Apache location and that Mod WSGI uses the python virtual environment that was built in the steps above. If the `--with-apxs` isn't specified Mod WSGI will scan the system to find where Apache is installed. Also if the `--with-python` isn't specified Mod WSGI will be built using the system python libraries instead of the OnRamp virtual environment.
    ```
    user@server:/# ./configure --with-apxs=ONRAMP/server/webserver/bin/apxs --with-python=ONRAMP/server/virtual-env/bin/python
    ```
- Build Mod WSGI from source via the following command
    ```
    user@server:/# make
    ```
    
- Install Mod WSGI into the specified Apache location via the following command
    ```
    user@server:/# make install
    ```
- Done the module will be installed in ONRAMP/server/webserver/modules/

---

### 4. MySQL Setup
MySQL is required by both Django and other pieces of OnRamp for communication and storage of state and information. The following instructions below cover setting up MySQL, hardening it for security, configuring it to work with Django, and moving it from the default installation.

- **Note:** For further documentation on MySQL and what the following commands do please read the link in the summary section of this documentation

##### How to install MySQL on Centos 7

- Install the MySQL community repository and then install MySQL and the development libraries via the following commands

    - **Note:** The first commands installs the MySQL community repository so we can install MySQL and the development libraries, and the other commands actually installs MySQL and the MySQL development libraries needed for it to run successfully.
    
    ```
    user@server:/# yum localinstall ONRAMPbuild/dependencies/mysql57-community-release-el7-7.noarch.rpm
    user@server:/# yum install -y mysql-community-server
    user@server:/# yum install -y mysql-community-devel
    ```

- Stop the running MySQL service and initialize a new data directory via the following commands
    - **Note:** The commands below stop MySQL and initialize a new **VALID** data directory for MySQL in the OnRamp server directory. This step is **VERY** important due to the fact that it creates the actual directory where data will be stored in addition to deal with all of the tedious tasks of setting up the correct permissions and owners for the directory and files.
    ```
    user@server:/# systemctl stop mysqld.service
    user@server:/# mysqld --initialize --user=mysql --datadir=ONRAMP/server/mysql
    ```

- *Optionally* remove the default MySQL directory to save space via the following command
    ```
    user@server:/# rm -r /var/lib/mysql
    ```

- Copy the OnRamp MySQL configuration file to the default location via the following command
    ```
    user@server:/# cp ONRAMP/server/build/config/my.cnf /etc/my.cnf
    ```
    
- Replace every instance of `ONRAMP` in `/etc/my.cnf` with `/path/to/onramp/`

- Fix SELinux so we can run MySQL under a different data directory
    - **Important:** If the following commands are not run MySQL **WILL NOT RUN** under a different directory other than its default location of `/var/lib/mysql`. The commands below tell SELinux that it is okay for MySQL to run out of a different directory. For more information on this look up the manuals for the commands via  `man semanage` and `man restorecon`
    ```
    user@server:/# semanage fcontext -a -s system_u -t mysqld_db_t "ONRAMP/server/mysql(/.*)?"
    user@server:/# restorecon -Rv ONRAMP/server/mysql
    ```
- Start up MySQL and everything should be running
    ```
    user@server:/# systemctl start mysqld.service
    ```

- Search `/var/log/mysqld.log` for the temporary password for MySQL
    - **Note:** The temporary password is created as a security measure for MySQL that way lazy users can't compromise the security of their database if they never change the default user and password.
    ```
    user@server:/# grep "temporary password" /var/log/mysqld.log
    ```
   
- Connect to MySQL with the temporary password and set a new one for the root user
    - **Note:** the --conect-expired-password is important here because without it you could not connect to mysql with the temporary password from the log.  
    ```
    user@server:/# mysql -u root --password=temp_password --conext-expired-password
    mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
    ```
    
- Login to MySQL with the newly changed password and harden it by removing defaults
    - **Note:** The following commands are necessary to remove all of the default users and tables that are created by MySQL on initialization. This step is technically *optionall** however, it is **recomended** that the following commands are run for security. 
    ```
    user@server:/# mysql -u root --password=new_password
    myqsl> DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')";
    myqsl> DELETE FROM mysql.user WHERE User='';
    myqsl> DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
    ```
- Create the user for django to use when connecting to the database and grant privileges
    - **Note:** The following commands create the user that is used by Django to talk to the database via the models. Without this user Django **CANNOT** talk to MySQL. The first command just creates the user with the password `OnRamp_16` and the second command makes sure the Django MySQL user has privileges to everything in the MySQL database.     
    ```
    myqsl> CREATE USER 'onramp'@'localhost' IDENTIFIED BY 'OnRamp_16;
    myqsl> GRANT ALL PRIVILEGES ON * . * TO 'onramp'@'localhost';
    ```
    
- Create the database for Django to store all of it's data in
    ```
    myqsl> CREATE DATABASE django;
    ```    
    
- Finally, flush the privileges so all changes to the users take effect
    ```
    myqsl> FLUSH PRIVILEGES;
    ```

---

### 5. Django Setup
The last step in the installation process of the OnRamp server is quite simple. The following instructions make sure all of the necessary tables are created in the MySQL database in addition to making sure an admin user is created that can login to OnRamp to configure OnRamp before regular users use it. 

- **Note:** For further documentation on Django and what the following commands do please read the link in the summary section of this documentation

##### How to setup Django
The following command is used to create all of the necessary tables in the MySQL database that was installed and configured above. This all happens vi the `manage.py` file which is a helpful tool provided by Django to do all of the heavy lifting. In addition to creating the databases the `manage.py` tool also creates `migrations` which are basically a change log/version control of all of the tables in a Django application. Through migrations, developers can modify tables with ease instead of writing custom SQL to modify tables.

- Run the following command to setup Django, migrations, and build the required MySQL tables
    - **Note:** In addition to creating the tables specified in the `models.py` files of the Django application that runs OnRamp, Django also creates their required tables as well with the following commands. 
    ```
    users@server:/# python ONRAMP/server/ui/manage.py migrate
    ```

##### How to create a Django admin user
An initial admin user is needed so that somebody can login to OnRamp. The following commands below are to create that initial Django admin user for OnRamp. The following code is the simplest way to do that. The username and password can be changed however and are not required to be `admin` and `admin123`. Change them to whatever you want for your installation if you choose to.
- Activate the virtual environment so we can import Django via the following command
    ```
    user@server:/# source ONRAMP/server/virtual-env/bin/activate 
    ```
    
- Open up a python shell via the following command
    ```
    users@server:/# python
    ```
    
- In the python shell run the following code to create the default admin user
    ```
    Python 2.7.5 (default, Sep 15 2016, 22:37:39) 
    [GCC 4.8.5 20150623 (Red Hat 4.8.5-4)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from django.contrib.auth.models import User
    >>> User.objects.create_superuser("admin", "", "admin123")
    ```
    
- Deactivate the virtual environment
    ```
    (virtual-env) [user@server:/#] deactivate
    ```

- Django setup is complete and a login to OnRamp should be available


---

##### Additional links for errors and debugging:
- http://docs.python-guide.org/en/latest/dev/virtualenvs/
- https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Deployment_Guide/ch-yum.html
- https://docs.djangoproject.com/en/1.10/intro/tutorial01/
- http://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html
- https://stackoverflow.com/questions/5841531/django-mod-wsgi-apache-importerror-at-no-module-named-djproj-urls/5841964#5841964
- http://www.tecmint.com/install-latest-mysql-on-rhel-centos-and-fedora/
- http://dev.mysql.com/doc/refman/5.7/en/resetting-permissions.html
- https://naveensnayak.wordpress.com/2016/01/14/changing-mysql-data-directory-centos-7/
- http://stackoverflow.com/questions/26474222/mariadb-10-centos-7-moving-datadir-woes
- https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql
- http://www.inmotionhosting.com/support/website/database-troubleshooting/error-1064
- http://stackoverflow.com/questions/19189813/setting-django-up-to-use-mysql
- https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/modwsgi/
- https://github.com/PyMySQL/mysqlclient-python
- https://mysqlclient.readthedocs.io/en/latest/
- http://www.cyberciti.biz/faq/how-do-i-empty-mysql-database/
- https://mysqlclient.readthedocs.io/en/latest/user_guide.html#introduction
- https://httpd.apache.org/docs/2.4/upgrading.html
- http://webpy.org/cookbook/mod_wsgi-apache-ubuntu
