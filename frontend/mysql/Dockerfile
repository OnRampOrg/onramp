FROM centos:centos7
LABEL maintainer="https://github.com/OnRampOrg"
LABEL name="Onramp Webserver"


ADD conf/requirements.txt /onramp/conf/requirements.txt
ADD conf/mysqlSetup.sql /onramp/conf/mysqlSetup.sql
ADD conf/mysqldSafeStart.sh /usr/bin/mysqldSafeStart
ADD conf/mysqlInitialStart.sh /usr/bin/mysqldInitialStart

# RUN yum -y update
# RUN yum clean all
RUN yum -y install gcc
RUN yum -y install epel-release

# hung on this command with the following output:
# warning: /var/cache/yum/x86_64/7/epel/packages/python-django-bash-completion-1.11.20-1.el7.noarch.rpm: Header V3 RSA/SHA256 Signature, key ID 352c64e5: NOKEY
# Public key for python-django-bash-completion-1.11.20-1.el7.noarch.rpm is not installed
# RUN yum -y install python2-devel python-pip python-django mysql
# RUN pip install virtualenv

RUN groupadd -r mysql && useradd -r -g mysql mysql
RUN yum -y install mysql-devel
RUN yum -y install mysql
RUN mkdir -p /var/run/mysqld
RUN chmod 777 /var/run/mysqld

RUN yum -y install mariadb-server
RUN /usr/libexec/mariadb-prepare-db-dir

RUN /usr/bin/mysqldInitialStart \
   && mysql < /onramp/conf/mysqlSetup.sql


# RUN yum -y install httpd
# RUN yum -y install mod_wsgi


WORKDIR /onramp
# RUN virtualenv -p /usr/bin/python2.7 ./venv
# RUN source ./venv/bin/activate \
#     && pip install -r ./conf/requirements.txt \
   #  && deactivate
RUN mkdir server

# RUN yum -y install apr-devel apr-util-devel pcre-devel zlib-devel openssl-devel
# VOLUME ["/var/lib/mysql"]

EXPOSE 80
# CMD [ "/bin/bash" ] 

