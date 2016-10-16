import django
django.setup()
import json


from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.template import Context
from django.template.loader import get_template





#============================== /admin/users/* ===============================#

# TODO wrapper
def users_page(request):
    """ Renders the users page on the Admin side

        URL: /admin/users

    :param request:
    :return:
    """
    context = Context({})
    template = get_template('admin_users.html')
    return HttpResponse(template.render(context))



def get_user(request):
    """ Gets all attributes for a specific user

        URL: /admin/users/Get

    :param request:
    :return:
    """
    post = request.POST.dict()
    user_id = post.get('user_id')
    if not user_id:
        # TODO error
        return HttpResponse()
    user = User.objects.get(id=user_id)
    if not user:
        # TOO error
        return HttpResponse()
    # TODO have to turn user into dict
    return HttpResponse(json.dumps(user))

def update_user(request):
    """ Updates attributes for a user

        URL: /admin/users/Update

    :param request:
    :return:
    """
    post = request.POST.dict()
    # TODO not implemented
    return HttpResponse()

def enable_user(request):
    """ Enables the specified user account

        URL: /admin/users/enable

    :param request:
    :return:
    """
    post = request.POST.dict()
    # TODO not implemented
    return HttpResponse()


def disable_user(request):
    """ Disables the specified user account

        URL: /admin/users/disable

    :param request:
    :return:
    """
    post = request.POST.dict()
    # TODO not implemented
    return HttpResponse()

def get_user_workspaces(request):
    """ Gets all workspaces for a specified user

        URL: /admin/users/workspaces

    :param request:
    :return:
    """
    return HttpResponse()


def get_user_jobs(request):
    """ Gets all jobs for a specified user

        URL: /admin/users/jobs

    :param request:
    :return:
    """
    return HttpResponse()

#=========================== /admin/workspaces/* =============================#

# TODO wrapper
def workspaces_page(request):
    """ Renders the workspaces page on the admin side

        URL: /admin/workspaces

    :param request:
    :return:
    """
    context = Context({})
    template = get_template('admin_workspaces.html')
    return HttpResponse(template.render(context))

# TODO wrapper
def pces_page(request):
    """ Renders the pce page on the admin side

        URL: /admin/pces

    :param request:
    :return:
    """
    context = Context({})
    template = get_template('admin_pce.html')
    return HttpResponse(template.render(context))

# TODO wrapper
def jobs_page(request):
    """ Renders the jobs page on the admin side

        URL: /admin/jobs

    :param request:
    :return:
    """
    context = Context({})
    template = get_template('admin_jobs.html')
    return HttpResponse(template.render(context))

# TODO wrapper
def modules_page(request):
    """ Renders the modules page on the admin side

        URL: /admin/modules

    :param request:
    :return:
    """
    context = Context({})
    template = get_template('admin_modules.html')
    return HttpResponse(template.render(context))