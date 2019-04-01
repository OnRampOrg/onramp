from django.conf.urls import url
import views


urlpatterns = [
    url(r'^GetUsers/$', views.get_all_users),
    url(r'^GetJobs/$', views.get_all_jobs),
    url(r'^GetWorkspaces/$', views.get_all_workspaces),
    url(r'^GetPces/$', views.get_all_pces),
    url(r'^GetModules/$', views.get_all_modules),
    
    url(r'^$', views.main),
]
