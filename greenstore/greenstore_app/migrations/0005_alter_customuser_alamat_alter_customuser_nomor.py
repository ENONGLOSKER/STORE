# Generated by Django 5.0.1 on 2024-01-22 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0004_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='alamat',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='nomor',
            field=models.CharField(max_length=20),
        ),
    ]