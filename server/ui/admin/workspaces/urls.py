from django.conf.urls import url
import views


urlpatterns = [
    url(r'^All$', views.get_all),
    url(r'^Jobs$', views.get_jobs),
    url(r'^PCEs$', views.get_pces),
    url(r'^Users$', views.get_users),
    url(r'^Create$', views.create_new_workspace),
    url(r'^AddPCEModPair$', views.add_pce_mod_pair),
    url(r'^$', views.main),
]