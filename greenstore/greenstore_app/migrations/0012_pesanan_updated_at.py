# Generated by Django 4.2.6 on 2024-02-11 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0011_remove_pesanan_user_alter_pesanan_nama_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesanan',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
