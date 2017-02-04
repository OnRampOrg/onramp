import json

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job
from core.definitions import JOB_STATES

# @login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    context = Context()
    template = get_template('admin_jobs.html')
    return HttpResponse(template.render(context))


# @login_required
def get_all_jobs(request):
    """ Gets all Jobs

    :param request:
    :return:
    """
    response = {
        'status':1,
        'status_message':'Success',
        'jobs':[]
    }
    curs = job.objects.all()
    for row in curs:
        response['jobs'].append({
            'job_id': row.job_id,
            'job_name': row.job_name,
            'username': row.user.username,
            'workspace_name': row.workspace.workspace_name,
            'pce_name': row.pce.pce_name,
            'module_name': row.module.module_name,
            'state': JOB_STATES.get(row.state, row.state),
            'output_file':row.output_file
        })
    return HttpResponse(json.dumps(response))