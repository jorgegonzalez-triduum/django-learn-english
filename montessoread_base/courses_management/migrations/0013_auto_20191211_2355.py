# Generated by Django 2.2.7 on 2019-12-12 04:55

from django.db import migrations, models
import triduum_resource.cross_app.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0012_remove_exercise_objects'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exercise',
            name='name',
        ),
        migrations.AddField(
            model_name='exercise',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='icon_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Icon name'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='image',
            field=triduum_resource.cross_app.fields.AutoWebpFileField(blank=True, null=True, upload_to='courses_management/exercise/', verbose_name='_(Category image)'),
        ),
        migrations.AddField(
            model_name='level',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='level',
            name='icon_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Icon name'),
        ),
        migrations.AddField(
            model_name='level',
            name='image',
            field=triduum_resource.cross_app.fields.AutoWebpFileField(blank=True, null=True, upload_to='courses_management/level/', verbose_name='_(Category image)'),
        ),
        migrations.AddField(
            model_name='section',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='icon_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Icon name'),
        ),
        migrations.AddField(
            model_name='section',
            name='image',
            field=triduum_resource.cross_app.fields.AutoWebpFileField(blank=True, null=True, upload_to='courses_management/sections/', verbose_name='_(Category image)'),
        ),
    ]