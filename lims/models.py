from django.db import models

class BoxModel(models.Model):
    pass

class PatientModel(models.Model):
    pid = models.CharField(unique=True, max_length=10)
    external_id = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pid

class SpecimenType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

class SpecimenModel(models.Model):
    patient = models.ForeignKey('PatientModel', on_delete=models.CASCADE)
    type = models.ForeignKey('SpecimenType', on_delete=models.CASCADE)
    collectdate = models.DateTimeField()
    collecttime = models.DateTimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

class AliquotType(models.Model):
    pass

class AliquotModel(models.Model):
    pass

