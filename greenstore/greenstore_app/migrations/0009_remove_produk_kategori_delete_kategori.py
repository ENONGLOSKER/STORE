# Generated by Django 5.0 on 2024-01-30 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('greenstore_app', '0008_kategori_alter_produk_kategori'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produk',
            name='kategori',
        ),
        migrations.DeleteModel(
            name='Kategori',
        ),
    ]