# Generated by Django 4.2.6 on 2024-02-11 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0012_pesanan_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesanan',
            name='diterima',
            field=models.BooleanField(default=False),
        ),
    ]
