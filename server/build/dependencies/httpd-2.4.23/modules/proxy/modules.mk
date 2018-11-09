libmod_proxy.la: mod_proxy.lo proxy_util.lo
	$(MOD_LINK) mod_proxy.lo proxy_util.lo $(MOD_PROXY_LDADD)
libmod_proxy_wstunnel.la: mod_proxy_wstunnel.lo
	$(MOD_LINK) mod_proxy_wstunnel.lo $(MOD_PROXY_WSTUNNEL_LDADD)
mod_proxy_hcheck.la: mod_proxy_hcheck.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_proxy_hcheck.lo $(MOD_PROXY_HCHECK_LDADD)
DISTCLEAN_TARGETS = modules.mk
static =  libmod_proxy.la libmod_proxy_wstunnel.la
shared =  mod_proxy_hcheck.la
