from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class CustomUser(AbstractUser):
    """
        Custom user stub in case of future user customization need
        Special thanks to wsvincent (and associated tutorial)
    """
    pass

class BoxModel(models.Model):
    name = models.CharField(max_length=50)
    length = models.IntegerField()
    height = models.IntegerField()


class StorageModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)


class VisitModel(models.Model):
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class SourceModel(models.Model):
    """
        Source depicts the external system (REDCap etc) that is generating
        the initial patient/visit information

        "local" depicts patients and visits created in LIMS rather than the
        external system (with data to be synced)

        A Django fixture is required to insert "local" as the first and default
        source (with other sources set up as a first step)
    """
    name = models.CharField(unique=True, max_length=80)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class PatientModel(models.Model):
    pid = models.CharField(unique=True, max_length=10)
    external_id = models.CharField(null=True, blank=True, max_length=40)
    source = models.ForeignKey('SourceModel', on_delete=models.CASCADE, default=1)
    synced = models.BooleanField(default=False)
    sync_date = models.DateTimeField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pid

    """
    Override default save:
    When the patient is created via an external system, automatically set the
    sync_date to the current time as it is automatically reconciled/synced
    """

    def save(self, *args, **kwargs):
        # if sync is set to true, set the time the sync occured
        if self.synced is True:
            self.sync_date = datetime.now()

        # call original save method
        super().save(*args, **kwargs)


class SpecimenType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class SpecimenModel(models.Model):

    patient = models.ForeignKey('PatientModel', on_delete=models.CASCADE)
    type = models.ForeignKey(
        'SpecimenType', related_name='types', on_delete=models.CASCADE)
    collectdate = models.DateTimeField()
    collecttime = models.TimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    volume = models.FloatField()


class AliquotType(models.Model):
    type = models.CharField(max_length=50)
    units = models.CharField(max_length=10)

    def __str__(self):
        return self.type


class AliquotModel(models.Model):

    specimen = models.ForeignKey('SpecimenModel', on_delete=models.CASCADE)
    type = models.ForeignKey(
        'AliquotType', related_name='types', on_delete=models.CASCADE)
    visit = models.ForeignKey('VisitModel',
                              on_delete=models.SET_NULL,
                              null=True)
    collectdate = models.DateTimeField()
    collecttime = models.TimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    volume = models.FloatField()
    notes = models.CharField(max_length=500, null=True)

    def __str__(self):
        # Access the name type instead of the primary key value
        return self.type.type
