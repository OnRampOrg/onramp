from django.conf.urls import url, include
from ui.public import views

urlpatterns = [
    url(r'^dashboard$', views.public_dashboard_page),
]
