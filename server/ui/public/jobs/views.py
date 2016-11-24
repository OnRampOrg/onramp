import json

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

from ui.admin.models import workspace, workspace_to_pce_module, job

from core.pce_connect import PCEAccess


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /public/Jobs/

    :param request:
    :return:
    """
    context = Context({'username': request.user})
    template = get_template('job_details.html')
    return HttpResponse(template.render(context))


@login_required
def get_job(request):
    return HttpResponse(json.dumps(request.POST.dict()))