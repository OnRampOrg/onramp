from django.conf.urls import url
import views

urlpatterns = [
    url(r'GetAll/$', views.get_all_pces),
    url(r'Add/$', views.add_pce),
    url(r'GetPCEModules/$', views.get_pce_modules),
    url(r'GetPCEWorkspaces/$', views.get_pce_workspaces),
    url(r'GetPCEJobs/$', views.get_pce_jobs),
    url(r'GetModuleState/$', views.get_module_state),
    url(r'DeployModule/$', views.deploy_module),
    #need to implement addmodule
    url(r'addmodule/$', views.add_module_to_pce),
    url(r'^$', views.main),
]