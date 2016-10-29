import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, pce

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