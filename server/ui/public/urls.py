from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^Dashboard/', include("ui.public.dashboard.urls")),
]
