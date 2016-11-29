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
    """ Gets information on the selected job

        URL:    /public/Jobs/GetJobInfo/
        TYPE:   POST

    :param request:
    :return:
    """
    post = request.POST.dict()
    job_id = post.get('job_id')
    if not job_id:
        response = {
            'status':False,
            'status_message':'No Job ID specified'
        }
        return HttpResponse(json.dumps(response))
    job_row = job.objects.get(job_id=int(job_id))
    conn = PCEAccess(job_row.pce.pce_id)
    status = conn.check_on_job(int(job_id))
    response = {
        'status':True,
        'status_message':'Success',
        'state':status['state_str'],
        'output':conn.read_job_output(int(job_id)),
        'file':status['output_file']
    }
    return HttpResponse(json.dumps(response))

@login_required
def get_user_jobs(request):
    """ Gets all jobs for the logged in user

        URL:    /public/Jobs/UserJobs
        TYPE:   GET

    :param request: Django request object
    :return: HttpResponse
    """
    username = request.user
    response = {
        'status':True,
        'status_message':'Success',
        'jobs':list(job.objects.filter(user__username=username).values())
    }
    return HttpResponse(json.dumps(response))
