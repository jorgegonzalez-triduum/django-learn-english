# Generated by Django 2.2.7 on 2019-12-01 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cross_app', '0007_auto_20191101_2032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appsection',
            options={'ordering': ['order']},
        ),
    ]
