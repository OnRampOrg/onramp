from django.conf.urls import url
import views


urlpatterns = [
    url(r'^All$', views.get_all),
    url(r'^AddUser$', views.add_user_to_workspace),
    url(r'^RemoveUser$', views.remove_user_from_workspace),
    url(r'^Jobs$', views.get_jobs),
    url(r'^PCEs$', views.get_pces),
    url(r'^WorkspaceUsers$', views.get_workspace_users),
    url(r'^PotentialUsers$', views.get_potential_users),
    url(r'^Create$', views.create_new_workspace),
    url(r'^Remove$', views.remove_workspace),
    url(r'^AddPCEModPair$', views.add_pce_mod_pair),
    url(r'^$', views.main),
]