# Generated by Django 5.0 on 2024-02-03 07:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0010_pesanan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pesanan',
            name='user',
        ),
        migrations.AlterField(
            model_name='pesanan',
            name='nama_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]