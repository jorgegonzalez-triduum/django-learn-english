# Generated by Django 2.2.9 on 2020-04-16 00:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0002_student_surname'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='birth_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Birth date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Male'), (2, 'Female')], verbose_name='Gender'),
        ),
    ]