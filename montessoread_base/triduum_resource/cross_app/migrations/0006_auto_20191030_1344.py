# Generated by Django 2.2.5 on 2019-10-30 18:44

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import triduum_resource.cross_app.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cross_app', '0005_auto_20191028_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinformation',
            name='dark_logo',
            field=triduum_resource.cross_app.fields.AutoWebpImageField(blank=True, null=True, upload_to='company_information/logos/', verbose_name='_(Dark logo)'),
        ),
        migrations.AddField(
            model_name='companyinformation',
            name='extra_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='_(Extra fields)'),
        ),
        migrations.AddField(
            model_name='companyinformation',
            name='light_logo',
            field=triduum_resource.cross_app.fields.AutoWebpImageField(blank=True, null=True, upload_to='company_information/logos/', verbose_name='_(Light logo)'),
        ),
        migrations.AddField(
            model_name='companyinformation',
            name='primary_color',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Primary color'),
        ),
        migrations.AddField(
            model_name='companyinformation',
            name='short_dark_logo',
            field=triduum_resource.cross_app.fields.AutoWebpImageField(blank=True, null=True, upload_to='company_information/logos/', verbose_name='_(Short light logo)'),
        ),
        migrations.AddField(
            model_name='companyinformation',
            name='short_light_logo',
            field=triduum_resource.cross_app.fields.AutoWebpImageField(blank=True, null=True, upload_to='company_information/logos/', verbose_name='_(Short light logo)'),
        ),
    ]
