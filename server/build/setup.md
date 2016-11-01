## OnRamp Build Instructions

##### Notes:
- This file documents everything that happens in the `install.py` file
- Most of the commands in this document should be run with sudo privileges

##### Important:
- Everywhere in this document where you see **ONRAMP** repace it with `/path/to/your/onramp/directory/`

---

### Python Virtual Environment

##### How to setup virtual environment

- First upgrade pip to make sure it's at the latest version (it will complain otherwise)
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

---

### Apache 2.4.X Setup

##### Centos 7 Dependencies

- Install the following required dependencies through yum 
```
user@server:/# yum install -y apr-devel
user@server:/# yum install -y apr-util-devel
user@server:/# yum install -y pcre-devel
user@server:/# yum install -y zlib-devel
user@server:/# yum install -y openssl-devel
user@server:/# yum install -y ptyhon-devel
```

##### How to install apache from source

- Un-tar apache source at `ONRAMP/server/build/dependencies/httpd-2.4.23.tar.gz`
- Run the following command below:
    ```
    user@server:/# ./configure \
    --prefix=ONRAMP/server/webserver \
    --enable-nonportable-atomics=yes \
    --with-mpm=worker \
    --enable-core=static \
    --enable-unixd=static \
    --enable-ssl=static \
    --enable-socache_shmcb=static \
    --enable-authz_core=static \
    --enable-allowmethods=static \
    --enable-headers=static \
    --enable-expires=static \
    --enable-alias=static \
    --enable-rewrite=static \
    --enable-filter=static \
    --enable-deflate=static \
    --enable-cache=static \
    --enable-log_config=static \
    --enable-mime=static \
    --enable-env=static \
    --disable-authn_core \
    --disable-authn_file \
    --disable-authz_host \
    --disable-authz_groupfile \
    --disable-authz_user \
    --disable-access_compat \
    --disable-mime_magic \
    --disable-auth_basic \
    --disable-setenvif \
    --disable-version \
    --disable-autoindex \
    --disable-dir
    ```
- Run `user@server:/# make`
- Run `user@server:/# make install`
- Copy over the httpd.conf to /path/to/apache/conf/httpd.conf and replace every instance of `ONRAMP` with the ONRAMP/server/webserver
- Copy over the httpd-vhosts.conf to /path/to/apache/conf/extra/httpd-vhosts.conf and replace every instance of `ONRAMP` with the full path to the OnRamp Directory

---

### Mod WSGI Setup

##### How to install Mod WSGI from source
- Install the python development libraries
    ```
    user@server:/# yum install python-devel
    ```
- Change to the directory where the .tar.gz file was downloaded
    ```
    user@server:/# cd ONRAMP/server/build/dependencies
    ```
    
- Un-tar the Mod WSGI source file with the following command 
    ```
    user@server:/# tar -zxpvf mod_wsgi-X.X.X.tar.gz
    ```
    
- cd into the un-tarred directory an run the following
    ```
    user@server:/# ./configure --with-apxs=ONRAMP/server/webserver/bin/apxs \
                    --with-python=ONRAMP/server/virtual-env/bin/python
    ```
- run `user@server:/# make`
- run `user@server:/# make install`
- Done the module will be installed in ONRAMP/server/webserver/modules/

---

### MySQL Setup

##### How to install MySQL on Centos 7

- Install the mysql community repository and then install MySQL and the development libraries
    ```
    user@server:/# yum localinstall /path/to/onramp/build/dependencies/mysql57-community-release-el7-7.noarch.rpm
    user@server:/# yum install -y mysql-community-server
    user@server:/# yum install -y mysql-community-devel
    ```

- Stop the running MySQL service and initialize a new data directory
    ```
    user@server:/# systemctl stop mysqld.service
    user@server:/# mysqld --initialize --user=mysql --datadir=/path/to/onramp/server/mysql
    ```

- Optionally remove the default MySQL directory to save space
    ```
    user@server:/# rm -r /var/lib/mysql
    ```

- Copy over the OnRamp MySQL configuration file and replace every instance of `ONRAMP` with `/path/to/onramp/`
    ```
    user@server:/# cp /path/to/onramp/build/config/my.cnf /etc/my.cnf
    ```

- Fix SELinux so we can run MySQL with a different data directory
    ```
    user@server:/# semanage fcontext -a -s system_u -t mysqld_db_t "/path/to/onramp/mysql(/.*)?"
    user@server:/# restorecon -Rv /path/to/onramp/mysql
    ```
- Start up MySQL and everything should be running
    ```
    user@server:/# systemctl start mysqld.service
    ```

- Search `/var/log/mysqld.log` for the temporary password to for MySQL
    ```
    user@server:/# grep "temporary password" /var/log/mysqld.log
    ```
   
- Connect to MySQL with the temporary password and set a new one
    ```
    user@server:/# mysql -u root --password=temp_password --conext-expired-password
    mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
    ```
    
- Login to MySQL with the newly changed password and harden it by removing defaults
    ```
    user@server:/# mysql -u root --password=new_password
    myqsl> DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')";
    myqsl> DELETE FROM mysql.user WHERE User='';
    myqsl> DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
    ```
- Create the user for django to use when connecting to the database and grant privileges
    ```
    myqsl> CREATE USER 'onramp'@'localhost' IDENTIFIED BY 'OnRamp_16;
    myqsl> GRANT ALL PRIVILEGES ON * . * TO 'onramp'@'localhost';
    ```
    
- Create the database for django to store all of it's data in
    ```
    myqsl> CREATE DATABASE django;
    ```    
    
- Finally flush the privileges so all changes to the users take effect
    ```
    myqsl> FLUSH PRIVILEGES;
    ```

---

### Django Setup

##### How to setup django

- Run `python /path/to/onramp/ui/manage.py migrate`

##### How to create django admin user

- Open up a python shell by typing `python`
- Run the following to create the default admin user
```
Python 2.7.5 (default, Sep 15 2016, 22:37:39) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from django.contrib.auth.models import User
>>> User.objects.create_superuser("admin", "", "admin123")
```

