libworker.la: worker.lo fdqueue.lo
	$(MOD_LINK) worker.lo fdqueue.lo
DISTCLEAN_TARGETS = modules.mk
static = libworker.la
shared =
