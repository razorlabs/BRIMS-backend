from django.db import models
from datetime import datetime
from lims.models.schedule import ScheduleModel

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

    def __str__(self):
        return self.name


class PatientModel(models.Model):
    pid = models.CharField(unique=True, max_length=10)
    external_id = models.CharField(null=True, blank=True, max_length=40)
    draw_schedule = models.ForeignKey('ScheduleModel', null=True, blank=True, on_delete=models.SET_NULL)
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

    Otherwise if patient already exists set sync and exit
    """

    def save(self, *args, **kwargs):
        # If patient was not created locally, check if patient already exists
        local_source = SourceModel.objects.get(name="local")
        if self.source == local_source:
            super().save(*args, **kwargs)
        if self.source != local_source:
            patient_exists = PatientModel.objects.filter(pid=self.pid)
            if(patient_exists.exists()):
                if(patient_exists.values("synced")[0]["synced"] is False):
                    patient_exists.update(
                        synced=True,
                        sync_date=datetime.now(),
                        source=self.source)
            else:
                self.synced=True
                self.sync_date=datetime.now()
                super().save(*args, **kwargs)



