from django.db import models

# Create your models here.
class Produk(models.Model):
    img_produk = models.ImageField(upload_to='produk')
    nama_produk = models.CharField(max_length=100)
    rettings = models.FloatField()
    harga = models.IntegerField()
    kategori = models.CharField(default='Elektronik',max_length=50)

    def __str__(self) -> str:
        return self.nama_produk