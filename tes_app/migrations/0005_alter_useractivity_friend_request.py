# Generated by Django 5.0.6 on 2024-09-18 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tes_app', '0004_alter_friendrequest_mode_useractivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivity',
            name='friend_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logged_activities', to='tes_app.friendrequest'),
        ),
    ]
