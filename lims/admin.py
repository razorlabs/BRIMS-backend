from django.contrib import admin

from . import models

admin.site.register(models.PatientModel)
admin.site.register(models.SpecimenModel)
admin.site.register(models.SpecimenType)
