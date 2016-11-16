import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, pce, module_to_pce, workspace_to_pce_module, job, module

from core.definitions import MODULE_STATES

from core.pce_connect import PCEAccess


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_pces.html')
    return HttpResponse(template.render(context))


@login_required
def get_all_pces(request):
    """ Gets All configured PCEs from the database

        URL: /admin/PCEs/GetAll

    :param request:
    :return:
    """
    response = {
        'status':0,
        'status_message':'Success',
        'pces':list(pce.objects.all().values())
    }
    return HttpResponse(json.dumps(response))

@login_required
def add_pce(request):
    """ Adds a new pce to the database
    
        URL: /admin/PCEs/Add/
    
    :param request: 
    :return: 
    """
    post = request.POST.dict()
    pce_obj, created = pce.objects.get_or_create(
        pce_name = post['name'],
        defaults={
            "ip_addr":post['url'],
            "ip_port":post['port'],
            "contact_info":post.get('contact_info', ''),
            "description":post.get('description', ''),
            "location":post.get('location', ''),
            "pce_username":post.get('pce_username')
        }
    )
    if created:
        response = {
            'status':0,
            'status_message':'Success'
        }
    else:
        response = {
            'status':1,
            'status_message':'A PCE with that name already exists, '
                             'please pick a unique name.'
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_pce_modules(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status':False, 'status_message':'No PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        pm_pairs = module_to_pce.objects.filter(pce_id=int(pce_id))
        modules = {}
        for pair in pm_pairs:
            module = pair.module
            if module.module_id in modules: continue
            modules[module.module_id] = {
                'module_name':module.module_name,
                'module_id':module.module_id,
                'description':module.description,
                'state':pair.state,
                'state_str':MODULE_STATES.get(pair.state, 'N/A'),
                'install_location':pair.install_location,
                'src_location_type':pair.src_location_type,
                'src_location_path':pair.src_location_path,
                'is_visible':pair.is_visible
            }
        response = {'status':True, 'status_message':'Success', 'modules':modules.values()}
    except Exception as e:
        response = {
            'status':False,
            'status_message':'Error retrieving requested data',
            'error_info':e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_pce_workspaces(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status': False, 'status_message': 'No PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        workspaces = {}
        for row in workspace_to_pce_module.objects.all():
            if row.pm_pair.pce.pce_id == int(pce_id):
                workspaces[row.workspace.workspace_id] = {
                    'workspace_name':row.workspace.workspace_name,
                    'workspace_id':row.workspace.workspace_id,
                    'description':row.workspace.description,
                }
        response = {'status':True, 'status_message':'Success', 'workspaces':workspaces.values()}
    except Exception as e:
        response = {
            'status':False,
            'status_message':'Error retrieving requested data',
            'error_info':e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_pce_jobs(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status': False, 'status_message': 'No PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        fields = ['job_id', 'pce_id', 'workspace_id', 'module_id', 'job_name', 'state']
        jobs = list(job.objects.filter(pce_id=int(pce_id)).values(*fields))
        response = {'status': True, 'status_message': 'Success', 'jobs':jobs}
    except Exception as e:
        response = {
            'status': False,
            'status_message': 'Error retrieving requested data',
            'error_info': e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_module_state(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    module_id = post.get('module_id')
    pce_id = post.get('pce_id')
    if not module_id or not pce_id:
        response = {'status': False, 'status_message': 'No Module ID and/or PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        row = module_to_pce.objects.get(pce_id=int(pce_id), module_id=int(module_id))
        response = {'status': True, 'status_message': 'Success',
                    'state_str': MODULE_STATES.get(row.state, 'N/A'), 'state':row.state}
    except Exception as e:
        response = {
            'status': False,
            'status_message': 'Error retrieving requested data',
            'error_info': e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def deploy_module(request):
    """

    :param request:
    :return:
    """
    post = request.POST.dict()
    module_id = post.get('module_id')
    pce_id = post.get('pce_id')
    if not module_id or not pce_id:
        response = {'status': False, 'status_message': 'No Module ID and/or PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        connector = PCEAccess(int(pce_id), "/tmp")
    except Exception as e:
        response = {'status':False, 'status_message':'Failed to create PCEAccess object',
                    'error_info':e.message}
        return HttpResponse(json.dumps(response))
    try:
        if connector.deploy_module(int(module_id)):
            response = {'status':True, 'status_message':'Successfully deployed module'}
        else:
            response = {'status': False, 'status_message': 'Failed to deployed module'}
    except Exception as e:
        response = {'status': False, 'status_message': 'Failed to deploy module',
                    'error_info': e.message}
    return HttpResponse(json.dumps(response))