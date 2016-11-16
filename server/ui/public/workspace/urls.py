from django.conf.urls import url
import views


urlpatterns = [
    url(r'^GetWorkspace/$', views.get_workspace),
    url(r'^GetPCEs/$', views.get_pces),
    url(r'^GetModules/$', views.get_modules_for_pce),
    url(r'^$', views.main),
]
