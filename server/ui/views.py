from django.http import HttpResponse
from django.template import loader

def login_page(request):
    context = {}
    template = loader.get_template("start.html")
    return HttpResponse(template.render(context, request))

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