import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from ui.admin.models import workspace, job

@staff_member_required(login_url='/')
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Workspaces

    :param request:
    :return:
    """
    template = get_template('admin_jobs.html')
    return HttpResponse(template.render({}, request))


@staff_member_required(login_url='/')
def get_all_jobs(request):
    """ Retrieve all Jobs

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

@staff_member_required(login_url='/')
def get_job(request):
    """ Retrieve a specific Job

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

@staff_member_required(login_url='/')
def create_job(request):
    """ Create a new job

        THIS IS TEMPORARY FOR TESTING

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

@staff_member_required(login_url='/')
def update_job(request):
    """ Updates a job with new fields
        
        URL: /admin/Jobs/Update

    :param request:
    :return:
    """
    post = request.POST.dict()
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
    job_obj.user = int(post.get('user'))
    job_obj.workspace = int(post.get('workspace'))
    job_obj.pce = int(post.get('pce'))
    job_obj.module = int(post.get('module'))
    job_obj.save()
    response = {'status': 1, 'status_message': 'Success'}
    return HttpResponse(json.dumps(response))

@staff_member_required(login_url='/')
def delete_job(request):
    """ Deletes a specific job

            URL: /admin/Jobs/Delete

        :param request:
        :return:
    """
    id = request.POST.dict().get("id")
    job.objects.filter(id=id).delete()
    response = {
        'status': 1,
        'status_message': 'Success'
    }
    return HttpResponse(json.dumps(response))
    
