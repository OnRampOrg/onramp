## Virtual Machine Setup

### Apache 2.4.X Setup

##### Dependencies
```
yum install -y apr-devel
yum install -y apr-util-devel
yum install -y pcre-devel
yum install -y zlib-devel
yum install -y openssl-devel
```

##### Install apache from source
 - todo: document how to do this

```
./configure \
--prefix=/OnRamp/webserver \
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

### Mod WSGI Setup
##### Install mod wsgi from source
- `yum install python-devel`
- cd to the directory where the .tar.gz file was downloaded
- untar the file with the following cmd `tar -zxpvf XXXX.tar.gz`
- cd into the un-tarred directory an run the following
```
./configure --with-apxs=/OnRamp/webserver/bin/apxs \
  --with-python=/OnRamp/virtual-env/bin/python
```
- run `make`
- run `make install`
- all done the module will be installed in ../webserver/modules/
