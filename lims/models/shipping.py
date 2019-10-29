from django.db import models

class ShipmentModel(models.Model):
    contents = models.ManyToManyField('AliquotModel')
    carrier = models.ForeignKey('CarrierModel',
                                on_delete=models.SET_NULL,
                                blank=True,
                                null=True)
    shipment_number = models.CharField(max_length=255, blank=True, null=True)
    # TODO What should we do if a destination is removed?
    destination = models.ForeignKey('DestinationModel',
                                    on_delete=models.SET_NULL,
                                    blank=True,
                                    null=True)
    sent_date = models.DateTimeField(blank=True, null=True)
    received_date = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

class DestinationModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CarrierModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

