
import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.template import Context
from django.template.loader import get_template
from ui.admin.models import job, workspace, pce, module

from core.definitions import JOB_STATES, PCE_STATES


@staff_member_required(login_url='/')
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Dashboard

    :param request:
    :return:
    """
    context = Context({'username':request.user})
    template = get_template('admin_dashboard.html')
    return HttpResponse(template.render(context))

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
    response = {
        'status':0,
        'status_message':'Success',
        'jobs':[]
    }
    curs = job.objects.all()
    for row in curs:
        response['jobs'].append({
            'job_id': row.job_id,
            'job_name': row.job_name,
            'user_id': row.user.id,
            'username': row.user.username,
            'workspace_id': row.workspace.workspace_id,
            'workspace_name': row.workspace.workspace_name,
            'pce_id': row.pce.pce_id,
            'pce_name': row.pce.pce_name,
            'module_id': row.module.module_id,
            'module_name': row.module.module_name,
            'state': JOB_STATES.get(row.state, row.state)
        })
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
        'pces':[]
    }
    curs = pce.objects.all().values("pce_id", "pce_name", "state", "location")
    for row in curs:
        response['pces'].append({
            'pce_id':row['pce_id'],
            'pce_name':row['pce_name'],
            'state':PCE_STATES.get(row['state'], row['state']),
            'location':row['location']
        })
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
