# Generated by Django 2.0.7 on 2018-08-01 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manager',
            name='update_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
