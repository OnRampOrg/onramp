import json

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job

from core.pce_connect import PCEAccess

# @login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    template = get_template('admin_jobs.html')
    return HttpResponse(template.render({}, request))


# @login_required
def get_all_jobs(request):
    """ Gets all Jobs

        URL: /admin/Jobs/GetAll

    :param request:
    :return:
    """
    response = {
        'status':1,
        'status_message':'Success',
        'jobs':list(job.objects.all().values())
    }
    return HttpResponse(json.dumps(response))

# @login_required
def get_job(request):
    """ Get a specific Job

        URL: /admin/Jobs/GetOne

    :param request:
    :return:
    """
    id = request.GET.dict().get("id")
    response = {
        'status': 1,
        'status_message': 'Success',
        'job': job.objects.filter(id=id)
    }
    return HttpResponse(json.dumps(response))

#working on this
#@login_required
def create_job(request):

    """ Creates a new Job and launches it

        URL: /admin/jobs/newjob/

    :param request:
    :return:
    """
    #data is in the body of the request
    post = json.loads(request.body)
    print(post)
    pce_id = post.get('pce_id')
    print(pce_id)
    response = json.loads(request.body)
    if not pce_id:
        response = {'status': False, 'status_message': 'No PCE ID specified'}
        return HttpResponse(json.dumps(response))

    try:
        connector = PCEAccess(int(pce_id))
        #TODO: need to add checking code
        #---------------------------------------------------

        #add job with module to a pce
        #user id may have to be username
        job_data = {
            'name': post.get('job_name'),
            'uioptions': "TODO"
        }
        response = connector.launch_a_job(int(post.get('user')), 1, int(post.get('module_id')), job_data)
        print(response)
    except Exception as e:
        response = {'status':False, 'status_message':'Failed to create PCEAccess object',
                    'error_info':e.message}
        return HttpResponse(json.dumps(response))

    

    return HttpResponse(json.dumps(response))













# @login_required
def update_job(request):
    """ Updates a job with new fields
        
        URL: /admin/Jobs/Update

    :param request:
    :return:
    """
    # TODO finish

# @login_required
def delete_job(request):
    """ Deletes a specific job

            URL: /admin/Jobs/Delete

        :param request:
        :return:
    """
    id = request.DELETE.dict().get("id")
    job.objects.filter(id=id).delete()
    response = {
        'status': 1,
        'status_message': 'Success'
    }
    return HttpResponse(json.dumps(response))
    
