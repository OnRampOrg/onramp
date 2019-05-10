import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def login_page(request):
    template = loader.get_template("start.html")
    return HttpResponse(template.render({}, request))

def about_page(request):
    template = loader.get_template("about.html")
    return HttpResponse(template.render({}, request))

def profile_page(request):
    template = loader.get_template("myprofile.html")
    return HttpResponse(template.render({}, request))

def contact_page(request):
    template = loader.get_template("contact.html")
    return HttpResponse(template.render({}, request))

def help_page(request):
    template = loader.get_template("help.html")
    return HttpResponse(template.render({}, request))

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
