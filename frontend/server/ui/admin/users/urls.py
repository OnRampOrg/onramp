from django.conf.urls import url
import views


urlpatterns = [
    url(r'^GetAll/$', views.get_all_users),
    url(r'^Create/$', views.create_user),
    url(r'^Update/$', views.update_user),
    url(r'^Disable/$', views.disable_user),
    url(r'^Enable/$', views.enable_user),
    url(r'^Jobs/$', views.get_user_jobs),
    url(r'^Workspaces/$', views.get_user_workspaces),
    url(r'^$', views.main),
]