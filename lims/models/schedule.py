from django.db import models
from django.contrib.postgres.fields import JSONField

"""
    Note: JSONField types are postgres specific
    Please reference:
    https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/
"""


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


