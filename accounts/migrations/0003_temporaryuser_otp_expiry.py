# Generated by Django 5.1.5 on 2025-01-21 17:47

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_temporaryuser_remove_user_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryuser',
            name='otp_expiry',
            field=models.DateTimeField(default=accounts.models.get_otp_expiry),
        ),
    ]
