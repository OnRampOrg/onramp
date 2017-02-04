import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie

from ui.admin.models import workspace, pce, module


@ensure_csrf_cookie
def login_page(request):
    context = RequestContext(request, {})
    template = loader.get_template("start.html")
    return HttpResponse(template.render(context))

def about_page(request):
    context = {}
    template = loader.get_template("about.html")
    return HttpResponse(template.render(context, request))

def profile_page(request):
    context = {}
    template = loader.get_template("myprofile.html")
    return HttpResponse(template.render(context, request))

def contact_page(request):
    context = {}
    template = loader.get_template("contact.html")
    return HttpResponse(template.render(context, request))

def help_page(request):
    context = {}
    template = loader.get_template("help.html")
    return HttpResponse(template.render(context, request))

def logout_view(request):
    logout(request)
    return login_page(request)

def onramp_login(request):
    post = request.POST.dict()
    response = {'status':-1, 'url':'', 'message':''}

    username = post['username']
    password = post['password']
    user = authenticate(username=username, password=password)
    if user is None:
        # failed authentication
        response['message'] = "Invalid username or password"
        return HttpResponse(json.dumps(response))
    response['status'] = 1
    login(request, user)
    if user.is_superuser or user.is_staff:
        response['url'] = 'admin/Dashboard/'
    else:
        response['url'] = 'public/Dashboard/'
    return HttpResponse(json.dumps(response))


def workspace_id_to_name(workspace_id):
    """ Get the name of a workspace from its ID

    :param workspace_id:
    :return:
    """
    ws_id = int(workspace_id)
    ws_row = workspace.objects.get(workspace_id=ws_id)
    return ws_row.workapce_name

def pce_id_to_name(pce_id):
    """ Get the name of a pce from its ID

    :param pce_id:
    :return:
    """
    p_id = int(pce_id)
    pce_row = pce.objects.get(pce_id=p_id)
    return pce_row.pce_name

def module_id_to_name(module_id):
    """ Get the name of a module from its ID

    :param module_id:
    :return:
    """
    mod_id = int(module_id)
    mod_row = module.objects.get(module_id=mod_id)
    return mod_row.module_name