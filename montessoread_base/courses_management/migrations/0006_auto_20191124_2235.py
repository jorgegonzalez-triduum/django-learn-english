# Generated by Django 2.2.5 on 2019-11-25 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0005_object'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiofile',
            name='model',
            field=models.IntegerField(choices=[(0, 'Alphabet'), (1, 'Category'), (2, 'Object')], default=0),
        ),
    ]