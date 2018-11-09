mod_vhost_alias.la: mod_vhost_alias.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_vhost_alias.lo $(MOD_VHOST_ALIAS_LDADD)
mod_negotiation.la: mod_negotiation.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_negotiation.lo $(MOD_NEGOTIATION_LDADD)
mod_actions.la: mod_actions.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_actions.lo $(MOD_ACTIONS_LDADD)
mod_speling.la: mod_speling.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_speling.lo $(MOD_SPELING_LDADD)
mod_userdir.la: mod_userdir.slo
	$(SH_LINK) -rpath $(libexecdir) -module -avoid-version  mod_userdir.lo $(MOD_USERDIR_LDADD)
libmod_alias.la: mod_alias.lo
	$(MOD_LINK) mod_alias.lo $(MOD_ALIAS_LDADD)
libmod_rewrite.la: mod_rewrite.lo
	$(MOD_LINK) mod_rewrite.lo $(MOD_REWRITE_LDADD)
DISTCLEAN_TARGETS = modules.mk
static =  libmod_alias.la libmod_rewrite.la
shared =  mod_vhost_alias.la mod_negotiation.la mod_actions.la mod_speling.la mod_userdir.la
