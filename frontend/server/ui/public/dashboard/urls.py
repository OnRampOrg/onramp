from django.conf.urls import url
import views


urlpatterns = [
    url(r'^GetWorkspaces/$', views.get_workspaces),
    url(r'^GetJobs/$', views.get_jobs),
    url(r'^$', views.main),
]
