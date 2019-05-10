from django.conf.urls import url
import views


urlpatterns = [

    url(r'^GetJobInfo/$', views.get_job),
    url(r'^UserJobs/$', views.get_user_jobs),
    url(r'^$', views.main),
]
