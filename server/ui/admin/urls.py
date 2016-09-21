from django.conf.urls import url, include
from ui.admin import views

urlpatterns = [
    url(r'^$', views.main)
]
