libmod_env.la: mod_env.lo
	$(MOD_LINK) mod_env.lo $(MOD_ENV_LDADD)
libmod_expires.la: mod_expires.lo
	$(MOD_LINK) mod_expires.lo $(MOD_EXPIRES_LDADD)
libmod_headers.la: mod_headers.lo
	$(MOD_LINK) mod_headers.lo $(MOD_HEADERS_LDADD)
mod_unique_id.la: mod_unique_id.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_unique_id.lo $(MOD_UNIQUE_ID_LDADD)
mod_remoteip.la: mod_remoteip.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_remoteip.lo $(MOD_REMOTEIP_LDADD)
DISTCLEAN_TARGETS = modules.mk
static =  libmod_env.la libmod_expires.la libmod_headers.la
shared =  mod_unique_id.la mod_remoteip.la
