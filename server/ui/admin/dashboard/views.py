
import json
import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.template import RequestContext
from django.template.loader import get_template
from django.shortcuts import render
from ui.admin.models import job, workspace, pce, module

from core.pce_connect import PCEAccess

#need to fix logger
#logger = logging.getLogger(__name__)



@staff_member_required(login_url='/')
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Dashboard

    :param request:
    :return:
    """
    template = get_template('admin_dashboard.html')
    return HttpResponse(template.render({'username': request.user}, request))

@staff_member_required(login_url='/')
def get_all_users(request):
    """ Retrieves all OnRamp users

        URL: /admin/Dashboard/GetUsers/

    :param request:
    :return:
    """
    users = User.objects.all().values('id', 'username', 'email', 'is_superuser')
    data = []
    for user in users:
        data.append({
            'user_id':user['id'],
            'username':user['username'],
            'email':user['email'],
            'is_admin':user['is_superuser']
        })
    response = {
        'status':0,
        'status_message':'Success',
        'users':data
    }
    
    return HttpResponse(json.dumps(response))

@staff_member_required(login_url='/')
def get_all_jobs(request):
    """ Gets basic info for all OnRamp Jobs

        URL: /admin/Dashboard/GetJobs/
        Description:
            This view returns basic information about all
            jobs that have been ran.

    :param request:
    :return:
    """
    ################# WORKING CODE
    connector = PCEAccess(int(1))
    connector.get_jobs(2)
    ##########################TEST CODE BELOW
    #connector.get_jobs(1)
    #try:
     #   connector = PCEAccess(int(1))
    #except Exception as e:
     #   response = {'status':False, 'status_message':'Failed to create PCEAccess object',
      #              'error_info':e.message}
       # return HttpResponse(json.dumps(response))

    # TODO In production this could be a lot of data may need to limit it somehow
    response = {
        'status':0,
        'status_message':'Success',
        'jobs':list(job.objects.all().defer("output_file").values())
        #sends a job to the client
        #'jobs': connector.get_jobs(1)
    }
    return HttpResponse(json.dumps(response))

@staff_member_required(login_url='/')
def get_all_workspaces(request):
    """ Gets all configured workspaces

        URL: /admin/Dashboard/GetWorkspaces/
        Description:
            This view returns basic information about all
            workspaces that have been configured on the server.

    :param request:
    :return:
    """
    response = {
        'status':0,
        'status_message':'Success',
        'workspaces':list(workspace.objects.all().values())
    }
    return HttpResponse(json.dumps(response))

@staff_member_required(login_url='/')
def get_all_pces(request):
    """ Gets all configured PCE's

        URL: /admin/Dashboard/GetPces/
        Description:
            This view returns basic information about all
            configured PCE's

    :param request:
    :return:
    """
    response = {
        'status':0,
        'status_message':'Success',
        'pces':list(pce.objects.all().values("pce_id", "pce_name", "state"))
    }
    return HttpResponse(json.dumps(response))

@staff_member_required(login_url='/')
def get_all_modules(request):
    """ Gets all loaded modules

        URL: /admin/Dashboard/GetModules/

    :param request:
    :return:
    """
    response = {
        'status':0,
        'status_message':'Success',
        'modules': list(module.objects.all().values("module_name", "module_id", "description"))
    }
    return HttpResponse(json.dumps(response))
