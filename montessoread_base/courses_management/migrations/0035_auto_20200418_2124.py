# Generated by Django 2.2.9 on 2020-04-19 02:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0034_auto_20200418_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playexercise',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classroom.Student'),
        ),
    ]
