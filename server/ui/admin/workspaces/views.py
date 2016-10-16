import json

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job, workspace_to_pce_module

# @login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_workspaces.html')
    return HttpResponse(template.render(context))

# @login_required
def get_all(request):
    """ Gets all workspaces

        URL: /admin/Workspaces/All/

    :param request:
    :return:
    """
    response = {
        'status':1,
        'status_message':'Success',
        'workspaces':list(workspace.objects.all().values())
    }
    return HttpResponse(json.dumps(response))

# @login_requried
def create_new_workspace(request):
    """ Adds a new workspace

    :param request:
    :return:
    """
    name = request.POST.get('name')
    if name is None:
        response = {'status':-1, 'status_message':'No name specified for new workspace.'}
    else:
        ws = workspace(workspace_name=name)
        ws.save()
        response = {
            'status':1,
            'status_message':'Success',
            'workspace':{'workspace_name':name, 'workspace_id':ws.id, 'description':ws.description}
        }
    return HttpResponse(json.dumps(response))

# @login_requried
def get_jobs(request):
    """ Gets all jobs for s specified workspace

        URL: /admin/Workspaces/Jobs

    :param request:
    :return:
    """
    workspace_id = request.POST.get('workspace_id')
    if workspace_id is None:
        response = {'status':-1, 'stauts_message':'No workspace_id specified'}
        return HttpResponse(json.dumps(response))
    response = {
        'status':1,
        'status_message':'Success',
        'jobs':list(job.objects.filter(workspace_id=workspace_id).values())
    }
    return HttpResponse(json.dumps(response))

# @login_requried
def get_pces(request):
    """ Gets all jobs for s specified workspace

        URL: /admin/Workspaces/PCEs

    :param request:
    :return:
    """
    workspace_id = request.POST.get('workspace_id')
    if workspace_id is None:
        response = {'status':-1, 'stauts_message':'No workspace_id specified'}
        return HttpResponse(json.dumps(response))

    response = {
        'status':1,
        'status_message':'Success',
        'pces':[] # TODO finish this (needs to be pce/module pairs)
    }
    return HttpResponse(json.dumps(response))

# @login_requried
def get_users(request):
    """ Gets all jobs for s specified workspace

        URL: /admin/Workspaces/Users

    :param request:
    :return:
    """
    workspace_id = request.POST.get('workspace_id')
    if workspace_id is None:
        response = {'status':-1, 'stauts_message':'No workspace_id specified'}
        return HttpResponse(json.dumps(response))

    response = {
        'status':1,
        'status_message':'Success',
        'users':[] # TODO finish query
    }
    return HttpResponse(json.dumps(response))


# @login_requried
def add_pce_mod_pair(request):
    """ Adds a PCE/Module pair to a workspace

        URL: /admin/Workspaces/AddPCEModPair

    :param request:
    :return:
    """
    workspace_id = request.POST.get('workspace_id')
    if workspace_id is None:
        response = {'status':-1, 'stauts_message':'No workspace_id specified'}
        return HttpResponse(json.dumps(response))
    module_id = request.POST.get('module_id')
    if workspace_id is None:
        response = {'status': -1, 'stauts_message': 'No module_id specified'}
        return HttpResponse(json.dumps(response))
    pce_id = request.POST.get('pce_id')
    if workspace_id is None:
        response = {'status': -1, 'stauts_message': 'No pce_id specified'}
        return HttpResponse(json.dumps(response))
    # TODO Save to the database

    response = {
        'status':1,
        'status_message':'Success',
        'data':{}
    }
    return HttpResponse(json.dumps(response))
