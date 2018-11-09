exp_exec_prefix = /home/admin/Desktop/onramp/server/webserver
exp_bindir = /home/admin/Desktop/onramp/server/webserver/bin
exp_sbindir = /home/admin/Desktop/onramp/server/webserver/bin
exp_libdir = /home/admin/Desktop/onramp/server/webserver/lib
exp_libexecdir = /home/admin/Desktop/onramp/server/webserver/modules
exp_mandir = /home/admin/Desktop/onramp/server/webserver/man
exp_sysconfdir = /home/admin/Desktop/onramp/server/webserver/conf
exp_datadir = /home/admin/Desktop/onramp/server/webserver
exp_installbuilddir = /home/admin/Desktop/onramp/server/webserver/build
exp_errordir = /home/admin/Desktop/onramp/server/webserver/error
exp_iconsdir = /home/admin/Desktop/onramp/server/webserver/icons
exp_htdocsdir = /home/admin/Desktop/onramp/server/webserver/htdocs
exp_manualdir = /home/admin/Desktop/onramp/server/webserver/manual
exp_cgidir = /home/admin/Desktop/onramp/server/webserver/cgi-bin
exp_includedir = /home/admin/Desktop/onramp/server/webserver/include
exp_localstatedir = /home/admin/Desktop/onramp/server/webserver
exp_runtimedir = /home/admin/Desktop/onramp/server/webserver/logs
exp_logfiledir = /home/admin/Desktop/onramp/server/webserver/logs
exp_proxycachedir = /home/admin/Desktop/onramp/server/webserver/proxy
EGREP = /usr/bin/grep -E
PCRE_LIBS = -lpcre
SHLTCFLAGS = -prefer-pic
LTCFLAGS = -prefer-non-pic -static
MKINSTALLDIRS = /home/admin/Desktop/onramp/server/webserver/build/mkdir.sh
INSTALL = $(LIBTOOL) --mode=install /home/admin/Desktop/onramp/server/webserver/build/install.sh -c
MATH_LIBS = -lm
CRYPT_LIBS = -lcrypt
DTRACE = true
PICFLAGS =
PILDFLAGS =
INSTALL_DSO = yes
ab_CFLAGS =
ab_LDFLAGS = -lssl -lcrypto -lpthread -ldl
NONPORTABLE_SUPPORT = checkgid fcgistarter
progname = httpd
OS = unix
SHLIBPATH_VAR = LD_LIBRARY_PATH
AP_BUILD_SRCLIB_DIRS =
AP_CLEAN_SRCLIB_DIRS =
HTTPD_VERSION = 2.4.23
HTTPD_MMN = 20120211
bindir = ${exec_prefix}/bin
sbindir = ${exec_prefix}/bin
cgidir = ${datadir}/cgi-bin
logfiledir = ${localstatedir}/logs
exec_prefix = ${prefix}
datadir = ${prefix}
localstatedir = ${prefix}
mandir = ${prefix}/man
libdir = ${exec_prefix}/lib
libexecdir = ${exec_prefix}/modules
htdocsdir = ${datadir}/htdocs
manualdir = ${datadir}/manual
includedir = ${prefix}/include
errordir = ${datadir}/error
iconsdir = ${datadir}/icons
sysconfdir = ${prefix}/conf
installbuilddir = ${datadir}/build
runtimedir = ${localstatedir}/logs
proxycachedir = ${localstatedir}/proxy
other_targets =
progname = httpd
prefix = /home/admin/Desktop/onramp/server/webserver
AWK = gawk
CC = gcc -std=gnu99
CPP = gcc -E
CXX =
CPPFLAGS =
CFLAGS =
CXXFLAGS =
LTFLAGS = --silent
LDFLAGS =
LT_LDFLAGS =
SH_LDFLAGS =
LIBS =
DEFS =
INCLUDES =
NOTEST_CPPFLAGS =
NOTEST_CFLAGS =
NOTEST_CXXFLAGS =
NOTEST_LDFLAGS =
NOTEST_LIBS =
EXTRA_CPPFLAGS = -DLINUX -D_REENTRANT -D_GNU_SOURCE
EXTRA_CFLAGS = -pthread
EXTRA_CXXFLAGS =
EXTRA_LDFLAGS =
EXTRA_LIBS =
EXTRA_INCLUDES = -I$(includedir) -I. -I/usr/include/apr-1
INTERNAL_CPPFLAGS =
LIBTOOL = /usr/lib64/apr-1/build/libtool --silent
SHELL = /bin/sh
RSYNC = /usr/bin/rsync
SH_LIBS =
SH_LIBTOOL = $(LIBTOOL)
MK_IMPLIB =
MKDEP = $(CC) -MM
INSTALL_PROG_FLAGS =
ENABLED_DSO_MODULES = ,reqtimeout,status
LOAD_ALL_MODULES = no
APR_BINDIR = /usr/bin
APR_INCLUDEDIR = /usr/include/apr-1
APR_VERSION = 1.4.8
APR_CONFIG = /usr/bin/apr-1-config
APU_BINDIR = /usr/bin
APU_INCLUDEDIR = /usr/include/apr-1
APU_VERSION = 1.5.2
APU_CONFIG = /usr/bin/apu-1-config