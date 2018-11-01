# Generated by Django 2.1.1 on 2018-11-01 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0013_auto_20181031_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='aliquotmodel',
            name='notes',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='aliquotmodel',
            name='visit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lims.VisitModel'),
        ),
    ]