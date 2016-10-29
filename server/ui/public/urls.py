from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^Dashboard/', include("ui.public.dashboard.urls")),
    url(r'^Workspace/', include("ui.public.workspace.urls")),
    url(r'^Jobs/', include("ui.public.dashboard.urls")),
]
