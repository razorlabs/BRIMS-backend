from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from lims.models.shipping import ShipmentModel

# TODO implement CSS icon display on frontend
class StorageModel(models.Model):
    """
       Storage objects can be contained in other storage objects ex) box, shelf
       Container points to the object a storage instance is contained in.
       A blank container represents a "top" object ex) building
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    # DO_NOTHING set to prevent NULL overwrite.
    # on_delete behavior handled by pre_delete below
    container = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)

    """
        css_icon should be equivalent to a css icon class to represent
        the storage object ex) warehouse (for semanitic-ui warehouse icon)
        https://react.semantic-ui.com/elements/icon/ (a port of font-awesome 5)
    """
    css_icon = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.name)

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
    description = models.CharField(max_length=255, blank=True, null=True)
    box_type = models.ForeignKey('BoxTypeModel', on_delete=models.CASCADE)
    # DO_NOTHING set to prevent NULL overwrite.
    # on_delete behavior handled by pre_delete below
    storage_location = models.ForeignKey('StorageModel',
                                         on_delete=models.DO_NOTHING,
                                         blank=True,
                                         null=True)
    manifest = models.ForeignKey('ShipmentModel',
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 null=True)
    def __str__(self):
        return str(self.name)


class BoxTypeModel(models.Model):
    """
        Describes box metadata (height/length/width/label etc)
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

# set child objects to parent object as new parent
# pre_delete prevents django admin from overwriting/ignoring this behavior
@receiver(signals.pre_delete, sender=StorageModel)
def set_child_storage_to_parent(sender, instance, *args, **kwargs):
    StorageModel.objects.filter(container=instance).update(container=instance.container)
    BoxModel.objects.filter(storage_location=instance).update(storage_location=instance.container)
