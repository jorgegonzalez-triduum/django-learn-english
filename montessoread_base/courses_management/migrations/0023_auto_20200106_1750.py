# Generated by Django 2.2.7 on 2020-01-06 22:50

import courses_management.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0022_auto_20200106_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiofile',
            name='alphabet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses_management.Alphabet'),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=courses_management.models.directory_path_audio, verbose_name='_(Audio file)'),
        ),
    ]