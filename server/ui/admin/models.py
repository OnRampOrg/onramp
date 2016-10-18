
from django.contrib.auth.models import User
from django.db import models

class workspace(models.Model):
    workspace_id = models.AutoField(primary_key=True)
    workspace_name = models.CharField(unique=True, max_length=255)
    description = models.TextField()


class pce(models.Model):
    pce_id = models.AutoField(primary_key=True)
    pce_name = models.CharField(unique=True, max_length=255)
    ip_addr = models.TextField(default='127.0.0.1')
    ip_port = models.IntegerField(default=0)
    state = models.IntegerField(default=0)
    contact_info = models.TextField(default='')
    location = models.TextField(default='')
    description = models.TextField(default='')
    pce_username = models.TextField(default='onramp') #TODO not sure if this is right

class module(models.Model):
    module_id = models.AutoField(primary_key=True)
    module_name = models.CharField(unique=True, max_length=255)
    version = models.TextField(default='')
    src_location = models.TextField(default='')
    description = models.TextField(default='')

class job(models.Model):
    job_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User)
    workspace_id = models.ForeignKey(workspace)
    pce_id = models.ForeignKey(pce)
    module_id = models.ForeignKey(module)
    job_name = models.TextField()
    state = models.IntegerField(default=0)
    output_file = models.TextField(default='') # TODO FileField or FilePathField?
    # TODO run_parameters, files, runtime

class user_to_workspace(models.Model):
    uw_pair_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User)
    workspace_id = models.ForeignKey(workspace)

    class Meta:
        unique_together = ('user_id', 'workspace_id')

class module_to_pce(models.Model):
    pm_pair_id = models.AutoField(primary_key=True)
    pce_id = models.ForeignKey(pce)
    module_id = models.ForeignKey(module)
    state = models.IntegerField(default=0)
    src_location_type = models.TextField(default='local')
    src_location_path = models.TextField(default='')
    install_location = models.TextField(default='')
    is_visible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pce_id', 'module_id')

class workspace_to_pce_module(models.Model):
    wpm_pair_id = models.AutoField(primary_key=True)
    workspace_id = models.ForeignKey(workspace)
    pm_pair_id = models.ForeignKey(module_to_pce)

    class Meta:
        unique_together = ('workspace_id', 'pm_pair_id')

