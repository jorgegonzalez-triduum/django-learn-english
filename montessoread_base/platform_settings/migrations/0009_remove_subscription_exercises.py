# Generated by Django 2.2.9 on 2020-04-26 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('platform_settings', '0008_auto_20200317_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='exercises',
        ),
    ]
