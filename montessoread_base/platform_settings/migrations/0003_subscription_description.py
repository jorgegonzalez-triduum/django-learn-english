# Generated by Django 2.2.7 on 2019-11-23 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_settings', '0002_subscription_months_term'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
