from django.core.exceptions import AppRegistryNotReady

# IMPORTANT: the following code needs to be here so we can import
# our models without having to call django.setup() in every single
# file that tries to import them
try:
    from django.apps import apps
    apps.check_apps_ready()
except AppRegistryNotReady:
    import django
    django.setup()
