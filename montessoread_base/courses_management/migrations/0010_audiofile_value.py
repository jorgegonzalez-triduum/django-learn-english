# Generated by Django 2.2.7 on 2019-12-01 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0009_auto_20191201_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiofile',
            name='value',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Value'),
        ),
    ]
