# Generated by Django 4.2.6 on 2024-02-11 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0013_pesanan_diterima'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesanan',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PROGRES', 'Progres'), ('DELIVERED', 'Delivered'), ('RETURN', 'Return')], default='PENDING', max_length=10),
        ),
    ]
