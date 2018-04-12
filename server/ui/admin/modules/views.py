import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace

@staff_member_required(login_url='/')
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    template = get_template('admin_modules.html')
    return HttpResponse(template.render({}, request))
