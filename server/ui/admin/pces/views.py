import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, pce, module_to_pce, workspace_to_pce_module, job, module

from core.definitions import MODULE_STATES

from core.pce_connect import PCEAccess

success_response = {'status': 1, 'status_message': 'Success'}

@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    template = get_template('admin_pces.html')
    return HttpResponse(template.render({}, request))


@login_required
def get_all_pces(request):
    """ Retrieve all configured PCEs

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
    """ Add a new PCE
    
        URL: /admin/PCEs/Add/
    
    :param request: 
    :return: 
    """
    post = request.POST.dict()
    pce_obj, created = pce.objects.get_or_create(
        pce_name = post['pce_name'],
        defaults={
            "ip_addr":post['ip_addr'],
            "ip_port":post['ip_port'],
            "contact_info":post.get('contact_info', ''),
            "description":post.get('description', ''),
            "location":post.get('location', ''),
            "pce_username":post.get('pce_username')
        }
    )
    if created:
        response = success_response
    else:
        response = {
            'status':-1,
            'status_message':'A PCE with that name already exists, '
                             'please pick a unique name.'
        }
    return HttpResponse(json.dumps(response))

@login_required
def edit_pce(request):
    """ Edit a specific PCE

        URL: /admin/PCEs/Edit
        
    :param request: 
    :return: 
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if pce_id is None:
        response = {'status': -1, 'status_message': 'No pce_id specified'}
        return HttpResponse(json.dumps(response))
    try:
        pce_obj = pce.objects.get(id = pce_id)
    except pce.DoesNotExist:
        response = {'status': -1, 'status_message': 'Invalid pce_id: {}'.format(pce_id)}
        return HttpResponse(json.dumps(response))
    pce_obj.pce_name = post.get('pce_name') #TODO unique check
    pce_obj.ip_addr = post.get('ip_addr')
    pce_obj.ip_port = post.get('ip_port')
    pce_obj.state = post.get('port')
    pce_obj.contact_info = post.get('contact_info')
    pce_obj.location = post.get('location')
    pce_obj.description = post.get('description')
    pce_obj.pce_username = post.get('pce_username')
    pce_obj.save()
    response = {'status': 1, 'status_message': 'Success'}
    return HttpResponse(json.dumps(response))

@login_required
def delete_pce(request):
    """ Delete a specific PCE

        URL: /admin/PCEs/Delete

    :param request:
    :return:
    """
    id = request.POST.dict().get("id")
    pce.objects.filter(id=id).delete()
    response = {'status': -1, 'status_message': 'Success'}
    return HttpResponse(json.dumps(response))

@login_required
def get_pce_modules(request):
    """ Retrieve all modules from a specific PCE
        URL: /admin/PCEs/Modules

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status': -1, 'status_message':'No PCE ID specified'}
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
        response = {'status': 1, 'status_message':'Success', 'modules':modules.values()}
    except Exception as e:
        response = {
            'status': -1,
            'status_message':'Error retrieving requested data',
            'error_info':e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def add_pce_module(request):
    """ Add a module to a specific PCE
        URL: /admin/PCEs/Module/Add

    :param request:
    :return:
    """
    post = request.POST.dict()
    mod_obj, created = module.objects.get_or_create(
        mod_name = post['module_name'],
        version = post.get('version', ''),
        src_location = post.get('src_location', ''),
        description = post.get('description', '')
    )

    if !created:
        response = {
            'status':-1,
            'status_message':'A Module with that name already exists, '
                             'please pick a unique name.'
        }
        return HttpResponse(json.dumps(response))

    pm_pair, created = module_to_pce.objects.get_or_create(
        pce_id = int(post['pce_id']),
        module_id = int(mod_obj.module_id)
    )
        
    if created:
        response = success_response
    else:
        response = {
            'status':-1,
            'status_message':'This module is already associated with this PCE'
        }
    return HttpResponse(json.dumps(response))

@login_required
def edit_pce_module(request):
    """ Edit a module

        URL: /admin/PCEs/Module/Edit

    :param request:
    :return:
    """
    post = request.POST.dict()
    mod_id = post.get('module_id')
    if mod_id is None:
        response = {'status': -1, 'status_message': 'No module_id specified'}
        return HttpResponse(json.dumps(response))
    try:
        mod_obj = module.objects.get(id = mod_id)
    except module.DoesNotExist:
        response = {'status': -1, 'status_message': 'Invalid module_id: {}'.format(mod_id)}
        return HttpResponse(json.dumps(response))
    mod_obj.module_name = post.get('name')
    mod_obj.version = post.get('version', '')
    mod_obj.src_location = post.get('src_location', '')
    mod_obj.description = post.get('description', '')
    mod_obj.save()
    return HttpResponse(json.dumps(success_response))

@login_required
def delete_pce_module(request):
    """ Delete Module

        URL: /admin/PCEs/Module/Delete

    :param request:
    :return:
    """
    id = request.POST.dict().get('id')
    module_to_pce.objects.filter(module_id=int(id)).delete()
    module.objects.filter(id=int(id)).delete()
    return HttpResponse(json.dumps(success_response))

@login_required
def get_pce_workspaces(request):
    """ Retrieve all workspaces for a specific PCE

        URL: /admin/PCEs/Workspaces

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status': -1, 'status_message': 'No PCE ID specified'}
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
        response = {'status':1, 'status_message':'Success', 'workspaces':workspaces.values()}
    except Exception as e:
        response = {
            'status':-1,
            'status_message':'Error retrieving requested data',
            'error_info':e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_pce_jobs(request):
    """
        URL: /admin/PCEs/Jobs

    :param request:
    :return:
    """
    post = request.POST.dict()
    pce_id = post.get('pce_id')
    if not pce_id:
        response = {'status': -1, 'status_message': 'No PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        fields = ['job_id', 'pce_id', 'workspace_id', 'module_id', 'job_name', 'state']
        jobs = list(job.objects.filter(pce_id=int(pce_id)).values(*fields))
        response = {'status': 1, 'status_message': 'Success', 'jobs':jobs}
    except Exception as e:
        response = {
            'status': -1,
            'status_message': 'Error retrieving requested data',
            'error_info': e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def get_module_state(request):
    """ Retrieve state of a specific module on specific a PCE

        URL: /admin/PCEs/Module/State

    :param request:
    :return:
    """
    post = request.POST.dict()
    module_id = post.get('module_id')
    pce_id = post.get('pce_id')
    if not module_id or not pce_id:
        response = {'status': -1, 'status_message': 'No Module ID and/or PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        row = module_to_pce.objects.get(pce_id=int(pce_id), module_id=int(module_id))
        response = {'status': 1, 'status_message': 'Success',
                    'state_str': MODULE_STATES.get(row.state, 'N/A'), 'state':row.state}
    except Exception as e:
        response = {
            'status': -1,
            'status_message': 'Error retrieving requested data',
            'error_info': e.message
        }
    return HttpResponse(json.dumps(response))

@login_required
def deploy_module(request):
    """ 

        URL: /admin/PCEs/Module/Deploy

    :param request:
    :return:
    """
    post = request.POST.dict()
    module_id = post.get('module_id')
    pce_id = post.get('pce_id')
    if not module_id or not pce_id:
        response = {'status': -1, 'status_message': 'No Module ID and/or PCE ID specified'}
        return HttpResponse(json.dumps(response))
    try:
        connector = PCEAccess(int(pce_id))
    except Exception as e:
        response = {'status': 1, 'status_message':'Failed to create PCEAccess object',
                    'error_info':e.message}
        return HttpResponse(json.dumps(response))
    try:
        if connector.deploy_module(int(module_id)):
            response = {'status':1, 'status_message':'Successfully deployed module'}
        else:
            response = {'status': -1, 'status_message': 'Failed to deployed module'}
    except Exception as e:
        response = {'status': -1, 'status_message': 'Failed to deploy module',
                    'error_info': e.message}
    return HttpResponse(json.dumps(response))



