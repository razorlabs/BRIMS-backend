from django.contrib import admin

from . import models

admin.site.register(models.PatientModel)
admin.site.register(models.SpecimenModel)
admin.site.register(models.SpecimenType)
admin.site.register(models.AliquotModel)
admin.site.register(models.AliquotType)
admin.site.register(models.VisitModel)
admin.site.register(models.SourceModel)
