/*
 * modules.c --- automatically generated by Apache
 * configuration script.  DO NOT HAND EDIT!!!!!
 */

#include "ap_config.h"
#include "httpd.h"
#include "http_config.h"

extern module core_module;
extern module authz_core_module;
extern module allowmethods_module;
extern module cache_module;
extern module socache_shmcb_module;
extern module so_module;
extern module filter_module;
extern module deflate_module;
extern module http_module;
extern module mime_module;
extern module log_config_module;
extern module env_module;
extern module expires_module;
extern module headers_module;
extern module proxy_module;
extern module proxy_wstunnel_module;
extern module ssl_module;
extern module mpm_worker_module;
extern module unixd_module;
extern module alias_module;
extern module rewrite_module;

/*
 *  Modules which implicitly form the
 *  list of activated modules on startup,
 *  i.e. these are the modules which are
 *  initially linked into the Apache processing
 *  [extendable under run-time via AddModule]
 */
module *ap_prelinked_modules[] = {
  &core_module,
  &authz_core_module,
  &allowmethods_module,
  &cache_module,
  &socache_shmcb_module,
  &so_module,
  &filter_module,
  &deflate_module,
  &http_module,
  &mime_module,
  &log_config_module,
  &env_module,
  &expires_module,
  &headers_module,
  &proxy_module,
  &proxy_wstunnel_module,
  &ssl_module,
  &mpm_worker_module,
  &unixd_module,
  &alias_module,
  &rewrite_module,
  NULL
};

/*
 *  We need the symbols as strings for <IfModule> containers
 */

ap_module_symbol_t ap_prelinked_module_symbols[] = {
  {"core_module", &core_module},
  {"authz_core_module", &authz_core_module},
  {"allowmethods_module", &allowmethods_module},
  {"cache_module", &cache_module},
  {"socache_shmcb_module", &socache_shmcb_module},
  {"so_module", &so_module},
  {"filter_module", &filter_module},
  {"deflate_module", &deflate_module},
  {"http_module", &http_module},
  {"mime_module", &mime_module},
  {"log_config_module", &log_config_module},
  {"env_module", &env_module},
  {"expires_module", &expires_module},
  {"headers_module", &headers_module},
  {"proxy_module", &proxy_module},
  {"proxy_wstunnel_module", &proxy_wstunnel_module},
  {"ssl_module", &ssl_module},
  {"mpm_worker_module", &mpm_worker_module},
  {"unixd_module", &unixd_module},
  {"alias_module", &alias_module},
  {"rewrite_module", &rewrite_module},
  {NULL, NULL}
};

/*
 *  Modules which initially form the
 *  list of available modules on startup,
 *  i.e. these are the modules which are
 *  initially loaded into the Apache process
 *  [extendable under run-time via LoadModule]
 */
module *ap_preloaded_modules[] = {
  &core_module,
  &authz_core_module,
  &allowmethods_module,
  &cache_module,
  &socache_shmcb_module,
  &so_module,
  &filter_module,
  &deflate_module,
  &http_module,
  &mime_module,
  &log_config_module,
  &env_module,
  &expires_module,
  &headers_module,
  &proxy_module,
  &proxy_wstunnel_module,
  &ssl_module,
  &mpm_worker_module,
  &unixd_module,
  &alias_module,
  &rewrite_module,
  NULL
};

