# Generated by Django 2.2.7 on 2019-11-23 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='months_term',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Months term'),
            preserve_default=False,
        ),
    ]
