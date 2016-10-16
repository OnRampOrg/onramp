from django.conf.urls import url
import views

urlpatterns = [

    url(r'^All$', views.get_all_jobs),
    url(r'^$', views.main),
]