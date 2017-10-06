import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job, workspace_to_pce_module, user_to_workspace

@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_workspaces.html')
    return HttpResponse(template.render(context))

@login_required
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

@login_required
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
            'workspace':{'workspace_name':name, 'workspace_id':ws.workspace_id, 'description':ws.description}
        }
    return HttpResponse(json.dumps(response))

@login_required
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

@login_required
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
    pce_mod_pairs = {}
    wpm_pairs = workspace_to_pce_module.objects.filter(workspace_id=int(workspace_id))
    for row in wpm_pairs:
        if row.pm_pair in pce_mod_pairs: continue
        module_obj = row.pm_pair.module
        pce_obj = row.pm_pair.pce
        pce_mod_pairs[row.pm_pair] = {
            'module_id':module_obj.module_id,
            'module_name':module_obj.module_name,
            'pce_id':pce_obj.pce_id,
            'pce_name':pce_obj.pce_name
        }
    response = {
        'status':True,
        'status_message':'Success',
        'pces':pce_mod_pairs.values()
    }
    return HttpResponse(json.dumps(response))



@login_required
def get_potential_users(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    if not post.get('workspace_id'):
        response = {'status':-1, 'status_message':'No workspace specified'}
        return HttpResponse(json.dumps(response))
    qs = user_to_workspace.objects.filter(workspace_id=int(post['workspace_id']))
    excluded_ids = [i.user.id for i in qs]
    response = {
        'status': 1,
        'status_message': 'Success',
        'users':[]
    }
    # we exclude admins because they cannot launch jobs anyways
    for row in User.objects.filter(is_superuser=False).exclude(id__in=excluded_ids).values('id', 'username'):
        response['users'].append({
            'user_id':row['id'],
            'username':row['username']
        })
    return HttpResponse(json.dumps(response))


@login_required
def get_workspace_users(request):
    """ Gets all users that have access to a specified workspace

        URL: /admin/Workspaces/Users

    :param request:
    :return:
    """
    workspace_id = request.POST.get('workspace_id')
    if workspace_id is None:
        response = {'status':-1, 'stauts_message':'No workspace_id specified'}
        return HttpResponse(json.dumps(response))
    qs = user_to_workspace.objects.filter(workspace_id=int(workspace_id))
    response = {
        'status':1,
        'status_message':'Success',
        'users':[{"user_id":i.user.id, "username":i.user.username} for i in qs]
    }
    return HttpResponse(json.dumps(response))

@login_required
def add_user_to_workspace(request):
    """ Give user permission to a specified workspace

        URL: /admin/Workspaces/AddUser

    :param request:
    :return:
    """
    post = request.POST.dict()
    if not post.get('workspace_id'):
        response = {'status':-1, 'status_message':"No workspace_id specified"}
        return HttpResponse(json.dumps(response))
    if not post.get('user_id'):
        response = {'status': -1, 'status_message': "No user_id specified"}
        return HttpResponse(json.dumps(response))
    row, created = user_to_workspace.objects.get_or_create(
        workspace_id=int(post['workspace_id']),
        user_id=int(post['user_id']))
    if created:
        response = {'status':1, 'status_message':'Success'}
    else:
        response = {'status':-1, 'status_message':"User already has permissions for this workspace."}
    return HttpResponse(json.dumps(response))

@login_required
def remove_user_from_workspace(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    if not post.get('workspace_id'):
        response = {'status': -1, 'status_message': "No workspace_id specified"}
        return HttpResponse(json.dumps(response))
    if not post.get('user_id'):
        response = {'status': -1, 'status_message': "No user_id specified"}
        return HttpResponse(json.dumps(response))
    user_to_workspace.objects.filter(workspace_id=int(post['workspace_id']), user_id=int(post['user_id'])).delete()
    response = {'status':1, 'status_message':"Success"}
    return HttpResponse(json.dumps(response))


@login_required
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
