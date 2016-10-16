import json

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace

# @login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_modules.html')
    return HttpResponse(template.render(context))
