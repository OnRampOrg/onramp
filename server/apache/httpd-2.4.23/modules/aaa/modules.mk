mod_authn_dbm.la: mod_authn_dbm.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authn_dbm.lo $(MOD_AUTHN_DBM_LDADD)
mod_authn_anon.la: mod_authn_anon.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authn_anon.lo $(MOD_AUTHN_ANON_LDADD)
mod_authn_dbd.la: mod_authn_dbd.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authn_dbd.lo $(MOD_AUTHN_DBD_LDADD)
mod_authn_socache.la: mod_authn_socache.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authn_socache.lo $(MOD_AUTHN_SOCACHE_LDADD)
mod_authz_dbm.la: mod_authz_dbm.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authz_dbm.lo $(MOD_AUTHZ_DBM_LDADD)
mod_authz_owner.la: mod_authz_owner.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authz_owner.lo $(MOD_AUTHZ_OWNER_LDADD)
mod_authz_dbd.la: mod_authz_dbd.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authz_dbd.lo $(MOD_AUTHZ_DBD_LDADD)
libmod_authz_core.la: mod_authz_core.lo
	$(MOD_LINK) mod_authz_core.lo $(MOD_AUTHZ_CORE_LDADD)
mod_authnz_ldap.la: mod_authnz_ldap.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_authnz_ldap.lo $(MOD_AUTHNZ_LDAP_LDADD)
mod_auth_form.la: mod_auth_form.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_auth_form.lo $(MOD_AUTH_FORM_LDADD)
mod_auth_digest.la: mod_auth_digest.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_auth_digest.lo $(MOD_AUTH_DIGEST_LDADD)
libmod_allowmethods.la: mod_allowmethods.lo
	$(MOD_LINK) mod_allowmethods.lo $(MOD_ALLOWMETHODS_LDADD)
DISTCLEAN_TARGETS = modules.mk
static =  libmod_authz_core.la libmod_allowmethods.la
shared =  mod_authn_dbm.la mod_authn_anon.la mod_authn_dbd.la mod_authn_socache.la mod_authz_dbm.la mod_authz_owner.la mod_authz_dbd.la mod_authnz_ldap.la mod_auth_form.la mod_auth_digest.la
