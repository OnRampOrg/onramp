import json
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

from ui.admin.models import workspace, workspace_to_pce_module, job

from core.pce_connect import PCEAccess


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /public/Workspace/

    :param request:
    :return:
    """
    context = Context({'username': request.user})
    template = get_template('workspace.html')
    return HttpResponse(template.render(context))


@login_required
def get_workspace(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    ws_id = post.get('workspace_id')
    if not ws_id:
        response = {
            'success':False,
            'status_message':'No workspace ID specified'
        }
        return HttpResponse(json.dumps(response))
    try:
        ws = workspace.objects.get(workspace_id=int(ws_id))
        response = {'success':True, 'data':{'workspace_name':ws.workspace_name, 'workspace_id':ws.workspace_id}}
    except Exception as e:
        response = {'success':False, 'status_message':'workspace with ID {} does not exist'.format(ws_id),
                    'error_info':e.message}
    return HttpResponse(json.dumps(response))

@login_required
def get_pces(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    ws_id = post.get('workspace_id')
    if not ws_id:
        # make sure we got a valid workspace id
        response = {
            'success': False,
            'status_message': 'No workspace ID specified'
        }
        return HttpResponse(json.dumps(response))
    try:
        pairs = workspace_to_pce_module.objects.filter(workspace_id=int(ws_id))
        pces = {}
        for wpm_pair in pairs:
            pce = wpm_pair.pm_pair.pce
            if pce.pce_id in pces: continue
            pces[pce.pce_id] = {
                'pce_id':pce.pce_id,
                'pce_name':pce.pce_name,
                'state':pce.state,
                'url':"{}:{}".format(pce.ip_addr, pce.ip_port)
            }
        response = {'success':True, 'status_message':'Success', 'pces':pces.values()}
    except Exception as e:
        response = {'success':False, 'status_message':'Error retrieving requested data',
                    'error_info':e.message}
    return HttpResponse(json.dumps(response))

@login_required
def get_modules_for_pce(request):
    """ Gets installed modules based on workspace/pce combination

    :param request:
    :return:
    """
    post = request.POST.dict()
    ws_id = post.get('workspace_id')
    pce_id = post.get('pce_id')
    if not ws_id or not pce_id:
        # make sure we got a valid workspace id
        response = {
            'success': False,
            'status_message': 'Missing workspace ID and/or pce ID'
        }
        return HttpResponse(json.dumps(response))
    try:
        # pce_access = PCEAccess(int(pce_id))
        # pce_access.refresh_module_states(int(pce_id))
        pairs = workspace_to_pce_module.objects.filter(workspace_id=int(ws_id))
        modules = {}
        for wpm_pair in pairs:
            pce = wpm_pair.pm_pair.pce
            if pce.pce_id != int(pce_id): continue
            module = wpm_pair.pm_pair.module
            modules[module.module_id] = {
                'module_id':module.module_id,
                'module_name':module.module_name,
                'description':module.description
            }
        response = {'success':True, 'status_message':'Success', 'modules':modules.values()}
    except Exception as e:
        response = {'success':False, 'status_message':'Error retrieving requested data',
                    'error_info':e.message}
    return HttpResponse(json.dumps(response))

@login_required
def get_module_options(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    module_id = post.get('module_id')
    if not pce_id or not module_id:
        # make sure we got a valid pce id and module id
        response = {
            'status': False,
            'status_message': 'No PCE/Module ID specified'
        }
        return HttpResponse(json.dumps(response))

    pce_access = PCEAccess(int(pce_id))
    pce_access.refresh_module_states(module_id=int(module_id))
    options = pce_access.get_module_uioptions(int(module_id), True)
    meta = pce_access.get_module_metadata(int(module_id), True)
    response = {
        'status':True,
        'status_message':'Success',
        'uioptions':options,
        'metadata':meta
    }
    return HttpResponse(json.dumps(response))

@login_required
def launch_job(request):
    """ Launches a job

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    module_id = post.get('module_id')
    workspace_id = post.get('workspace_id')
    job_name = post.get('job_name')
    options = json.loads(post.get('uioptions', "{}"))
    job_data = {
        'name':job_name,
        'uioptions':options
    }

    user = User.objects.get(username=request.user)

    pce_conn = PCEAccess(int(pce_id))
    pce_conn.refresh_module_states(int(module_id))
    resp = pce_conn.launch_a_job(user.id, int(workspace_id), int(module_id), job_data)

    resp['status'] = True
    resp['status_message'] = 'Success'
    return HttpResponse(json.dumps(resp))