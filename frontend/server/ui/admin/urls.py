from django.conf.urls import url, include


urlpatterns = [
    url(r'^Dashboard/', include("ui.admin.dashboard.urls")),
    url(r'^Users/', include("ui.admin.users.urls")),
    url(r'^Jobs/', include("ui.admin.jobs.urls")),
    url(r'^PCEs/', include("ui.admin.pces.urls")),
    url(r'^Workspaces/', include("ui.admin.workspaces.urls")),
    # url(r'^Modules/', include("ui.admin.modules.urls")),
]
