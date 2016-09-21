from django.http import HttpResponse
from django.template import loader

def public_dashboard_page(request):
    context = {}
    template = loader.get_template("user_dashboard.html")
    return HttpResponse(template.render(context, request))


