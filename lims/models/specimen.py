from django.db import models
from lims.models.patient import PatientModel

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
