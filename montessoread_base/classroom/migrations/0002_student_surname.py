# Generated by Django 2.2.7 on 2020-04-06 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='surname',
            field=models.CharField(default='', max_length=50, verbose_name='Surname'),
            preserve_default=False,
        ),
    ]
