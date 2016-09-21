mod_session.la: mod_session.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_session.lo $(MOD_SESSION_LDADD)
mod_session_cookie.la: mod_session_cookie.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_session_cookie.lo $(MOD_SESSION_COOKIE_LDADD)
mod_session_crypto.la: mod_session_crypto.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_session_crypto.lo $(MOD_SESSION_CRYPTO_LDADD)
mod_session_dbd.la: mod_session_dbd.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_session_dbd.lo $(MOD_SESSION_DBD_LDADD)
DISTCLEAN_TARGETS = modules.mk
static = 
shared =  mod_session.la mod_session_cookie.la mod_session_crypto.la mod_session_dbd.la
