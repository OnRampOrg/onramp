


import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import job, user_to_workspace

@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Dashboard

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_users.html')
    return HttpResponse(template.render(context))

# @login_required
def get_all_users(request):
    """ Retrieves all OnRamp users

        URL: /admin/Dashboard/GetUsers/

    :param request:
    :return:
    """
    users = User.objects.all().values('id', 'first_name', 'last_name', 'username', 'email', 'is_superuser', 'is_active')
    data = []
    for user in users:
        data.append({
            'user_id':user['id'],
            'username':user['username'],
            'first_name':user['first_name'],
            'last_name':user['last_name'],
            'is_enabled':user['is_active'],
            'email':user['email'],
            'is_admin':user['is_superuser']
        })
    response = {
        'status':0,
        'status_message':'Success',
        'users':data
    }
    return HttpResponse(json.dumps(response))

# @login_required
def update_user(request):
    """ Updates the specified user with new settings

        URL: /admin/Users/Update/

    :param request:
    :return:
    """
    post = request.POST.dict()
    user = post.get('user_id')
    if user is None:
        response = {'status':-1, 'status_message':'No user_id specified'}
        return HttpResponse(json.dumps(response))
    try:
        user_obj = User.objects.get(id=user)
    except User.DoesNotExist:
        response = {'status':-1, 'status_message':'Invalid user_id: {}'.format(user)}
        return HttpResponse(json.dumps(response))
    user_obj.first_name = post.get('first_name')
    user_obj.last_name = post.get('last_name')
    password = post.get('password')
    if password and password != "**********":
        # update the password
        user_obj.set_password(password)
    if post.get('username'):
        user_obj.username = post['username']
    user_obj.email = post.get('email')
    user_obj.is_superuser = json.loads(post.get('is_admin', 'false'))
    user_obj.is_active = json.loads(post.get('is_enabled', 'false'))
    user_obj.save()
    response = {'status':1, 'status_message':'Success'}
    return HttpResponse(json.dumps(response))


# @login_required
def create_user(request):
    """ Creates a new user with specified settings

        URL: /admin/Users/Create/

    :param request:
    :return:
    """
    post = request.POST.dict()
    username = post.get('username')
    if username is None:
        response = {'status':-1, 'status_message':'No username specified.'}
        return HttpResponse(json.dumps(response))
    password = post.get('password')
    if password is None:
        response = {'status': -1, 'status_message': 'No password specified.'}
        return HttpResponse(json.dumps(response))
    user_obj = User(
        username=username,
        first_name=post.get('first_name'),
        last_name=post.get('last_name'),
        email=post.get('email'),
        is_superuser=json.loads(post.get('is_admin', 'false')),
        is_active=json.loads(post.get('is_enabled', 'false'))
    )
    user_obj.set_password(password)
    user_obj.save()
    response = {'status':1, 'status_message':'Success'}
    return HttpResponse(json.dumps(response))


# @login_required
def disable_user(request):
    """ Disables the specified user account so they cannot login

        URL: /admin/Users/Disable

    :param request:
    :return:
    """
    user_id = request.POST.get('user_id')
    if user_id is None:
        response = {'status':-1, 'status_message':'No user_id specified.'}
        return HttpResponse(json.dumps(response))
    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        response = {'status':-1, 'status_message':'No user with id {} exists'.format(user_id)}
        return HttpResponse(json.dumps(response))
    user_obj.is_active = False
    user_obj.save()
    response = {'status':1, 'status_message':'Success'}
    return HttpResponse(json.dumps(response))


# @login_required
def get_user_jobs(request):
    """ Gets all jobs ran by a specific user

        URL: /admin/Users/Jobs

    :param request:
    :return:
    """
    post = request.POST.dict()
    user = post.get('user_id')
    if not user:
        response = {'status':-1, 'status_message':'No user supplied'}
        return HttpResponse(json.dumps(response))
    response = {
        'status':1,
        'status_message':'Success',
        'jobs': list(job.objects.filter(user_id=user).defer('output_file'))
    }
    return HttpResponse(json.dumps(response))

# @login_required
def get_user_workspaces(request):
    """ Gets all workspaces for a given user

        URL: /admin/Users/Workspaces

    :param request:
    :return:
    """
    post = request.POST.dict()
    user = post.get('user_id')
    if not user:
        response = {'status': -1, 'status_message': 'No user supplied'}
        return HttpResponse(json.dumps(response))
    response = {
        'status': 1,
        'status_message': 'Success',
        'workspaces':[]
    }
    qs = user_to_workspace.objects.filter(user_id=user)
    for row in qs:
        response['workspaces'].append({
            'workspace_id':row.workspace_id.workspace_id,
            'workspace_name':row.workspace_id.workspace_name,
            'description':row.workspace_id.description
        })
    return HttpResponse(json.dumps(response))