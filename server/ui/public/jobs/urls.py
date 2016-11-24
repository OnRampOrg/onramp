from django.conf.urls import url
import views


urlpatterns = [

    url(r'^GetJobInfo/$', views.get_job),
    url(r'^$', views.main),
]
