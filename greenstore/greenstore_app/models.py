from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    nomor = models.CharField(max_length=20)
    alamat = models.CharField(max_length=255)

class Kategori(models.Model):
    kategori = models.CharField(max_length=100)

    def __str__(self):
        return self.kategori

class Produk(models.Model):
    img_produk = models.ImageField(upload_to='produk')
    nama_produk = models.CharField(max_length=100)
    rettings = models.FloatField()
    harga = models.IntegerField()
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, default=1)  # Ganti 1 dengan ID kategori default
    stok = models.IntegerField(default=0)

    def __str__(self):
        return self.nama_produk
    
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField('Produk', through='CartItem')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    produk = models.ForeignKey('Produk', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
