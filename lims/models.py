from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from datetime import datetime

"""
    Note: Many of the field types are postgres specific
    Please reference:
    https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/
"""


class CustomUser(AbstractUser):
    """
        Custom user stub in case of future user customization need
        Special thanks to WSVincent (and associated tutorial)
    """
    pass


# patient scheduleing models
class EventModel(models.Model):
    """
        A scheduled event in a study
        ex) week 1 visit
        ex) baseline visit
        order: depicts order of display in draw/event grid
    """

    event = models.CharField(max_length=120, unique=True)
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.event


class SpecimenType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

# eventually https://python-jsonschema.readthedocs.io/en/stable/ should be implemented
# TODO override create/save function to check against Specimen/Event

class ScheduleModel(models.Model):
    name = models.CharField(max_length=255)
    schedule = JSONField()

    def __str__(self):
        return self.name

# Storage related models
class BoxSlotModel(models.Model):
    """
        Slot in a box model
    """
    row_position = models.IntegerField('Row position')
    column_position = models.IntegerField('Column position')
    box = models.ForeignKey('BoxModel', on_delete=models.CASCADE)
    content = models.OneToOneField('AliquotModel',
                                   unique=True,
                                   on_delete=models.CASCADE)

#    def __str__(self):
#        return str(self.content.id)
#
    # write save method that checks position of box

class BoxModel(models.Model):
    """
        Indivdual instance of a box
    """

    name = models.CharField(max_length=50)
    decription = models.CharField(max_length=255, blank=True, null=True)
    box_type = models.ForeignKey('BoxTypeModel', on_delete=models.CASCADE)


class BoxTypeModel(models.Model):
    """
        Describes box meta data
    """

    numbered = 'numeric'
    az = 'alphabetic'
    LABEL_CHOICES = (
        (az, 'A-Z'),
        (numbered, 'Numbered'),
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    length = models.IntegerField(default=2)
    height = models.IntegerField(default=2)
    length_label = models.CharField(
        max_length=8,
        choices=LABEL_CHOICES,
        default=numbered)
    height_label = models.CharField(
        max_length=8,
        choices=LABEL_CHOICES,
        default=numbered)
    length_inverted = models.BooleanField(default=False)
    height_inverted = models.BooleanField(default=False)

# make delete set parent name to overhead child


class StorageModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)


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




class SpecimenModel(models.Model):

    patient = models.ForeignKey('PatientModel', on_delete=models.CASCADE)
    type = models.ForeignKey(
        'SpecimenType', related_name='types', on_delete=models.CASCADE)
    collectdate = models.DateField()
    collecttime = models.TimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    volume = models.FloatField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return("{patient} {type}".format(patient=self.patient.pid, type=self.type))


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
