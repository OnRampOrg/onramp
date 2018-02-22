from django.conf.urls import url
import views

urlpatterns = [
    url(r'^GetAll$', views.get_all_jobs),
    url(r'^GetOne$', views.get_job),
    url(r'^Create$', views.create_job),
    url(r'^Update$', views.update_job),
    url(r'^Delete$', views.delete_job),
    url(r'^$', views.main),
]
