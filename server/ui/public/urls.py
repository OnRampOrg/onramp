from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^dashboard$', views.public_dashboard_page),
]
