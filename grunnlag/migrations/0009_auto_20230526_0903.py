# Generated by Django 3.2.19 on 2023-05-26 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grunnlag', '0008_auto_20230526_0901'),
    ]

    operations = [
        migrations.RenameField(
            model_name='camera',
            old_name='sensor_size_unit',
            new_name='physical_sensor_size_unit',
        ),
        migrations.AddField(
            model_name='camera',
            name='physical_sensor_size_x',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='physical_sensor_size_y',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
