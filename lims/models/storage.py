from django.db import models


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

# make delete set parent name to overhead child


class StorageModel(models.Model):
    """
       Storage objects can be contained in other storage objects ex) box, shelf
       Parent points to the object a storage instance is contained in.
       A blank parent represents a "top" object ex) building
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    """
        css_icon should be equivalent to a css icon class to represent
        the storage object ex) warehouse (for semanitic-ui warehouse icon)
        https://react.semantic-ui.com/elements/icon/ (a port of font-awesome 5)
    """
    css_icon = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.name)
