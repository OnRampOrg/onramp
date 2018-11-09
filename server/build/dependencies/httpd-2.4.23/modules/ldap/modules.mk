mod_ldap.la: util_ldap.slo util_ldap_cache.slo util_ldap_cache_mgr.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  util_ldap.lo util_ldap_cache.lo util_ldap_cache_mgr.lo $(MOD_LDAP_LDADD)
DISTCLEAN_TARGETS = modules.mk
static = 
shared =  mod_ldap.la
