import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

from ui.admin.models import user_to_workspace, job

from core.definitions import JOB_STATES


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Dashboard/

    :param request:
    :return:
    """
    context = Context({'username': request.user})
    template = get_template('user_dashboard.html')
    return HttpResponse(template.render(context))


@login_required
def get_workspaces(request):
    """ Gets all workspaces for the logged in user

        URL: /public/Dashboard/GetWorkspaces

    :param request:
    :return:
    """

    ws_qs = user_to_workspace.objects.filter(user_id=request.user.id)
    response = {
        'status':0,
        'status_message':'Success',
        'workspaces':[{
            'workspace_id':i.workspace.workspace_id,
            'workspace_name':i.workspace.workspace_name
        } for i in ws_qs]
    }
    return HttpResponse(json.dumps(response))

@login_required
def get_jobs(request):
    """ Gets all jobs for the logged in user

        URL: /public/Dashboard/GetJobs

    :param request:
    :return:
    """
    response = {
        'status':0,
        'status_message':'Success',
        'jobs':[]
    }
    curs = job.objects.filter(user_id=request.user.id)
    for row in curs:
        response['jobs'].append({
            'job_id':row.job_id,
            'job_name':row.job_name,
            'user_id':row.user.id,
            'username':row.user.username,
            'workspace_id':row.workspace.workspace_id,
            'workspace_name':row.workspace.workspace_name,
            'pce_id':row.pce.pce_id,
            'pce_name':row.pce.pce_name,
            'module_id':row.module.module_id,
            'module_name':row.module.module_name,
            'state':JOB_STATES.get(row.state, row.state)
        })
    return HttpResponse(json.dumps(response))