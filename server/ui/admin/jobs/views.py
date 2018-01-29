import json

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job

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

# @login_required
def create_job(request):
    """ Create a new job

        URL: /admin/Jobs/Create

    :param request:
    :return:
    """
    post = request.POST.dict()
    job_obj = job.objects.create(
        job_name = post.get('job_name')
    )
    job_obj.state = post.get('state')
    job_obj.output_file = post.get('output_file')
    # TODO add foreign key fields

    job_obj.save()
    response = {'status': 1, 'status_message': 'Success'}
    return HttpResponse(json.dumps(response))

# @login_required
def update_job(request):
    """ Updates a job with new fields
        
        URL: /admin/Jobs/Update

    :param request:
    :return:
    """
    post = request.PUT.dict()
    job_id = post.get('job_id')
    if job_id is None:
        response = {'status': -1, 'status_message': 'No job_id specified'}
        return HttpResponse(json.dumps(response))
    try: 
        job_obj = job.objects.get(id = job_id)
    except job.DoesNotExist:
        response = {'status': -1, 'status_message': 'Invalid job_id: {}'.format(jobId)}
        return HttpResponse(json.dumps(response))
    job_obj.job_name = post.get('job_name')
    job_obj.state = post.get('state')
    job_obj.output_file = post.get('output_file')
    # TODO add the rest of the fields
    job_obj.save()
    response = {'status': 1, 'status_message': 'Success'}
    return HttpResponse(json.dumps(response))

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
    
