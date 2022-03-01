# Generated by Django 2.2.5 on 2020-06-17 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses_management', '0041_auto_20200616_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='exercise_type',
            field=models.PositiveIntegerField(choices=[(1, 'Pronunciation'), (2, 'Rhyming images'), (3, 'Correct image'), (4, 'Rhyming images (2 - 2)'), (5, 'Alphabet sounds'), (6, 'Blending'), (7, 'Blending basic'), (8, 'Beggining sounds')], default=1, verbose_name='Exercise type'),
        ),
    ]