# Generated by Django 2.1.1 on 2018-09-18 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0009_auto_20180917_2218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='specimenmodel',
            old_name='type',
            new_name='type_id',
        ),
    ]
