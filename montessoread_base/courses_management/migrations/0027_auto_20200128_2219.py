# Generated by Django 2.2.7 on 2020-01-29 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0026_delete_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playexercise',
            name='results',
        ),
        migrations.AlterField(
            model_name='playexercisestatus',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Created'), (2, 'Playing'), (3, 'Terminated')], verbose_name='Status'),
        ),
    ]
