from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    nomor = models.CharField(max_length=20)
    alamat = models.CharField(max_length=255)

class Produk(models.Model):
    img_produk = models.ImageField(upload_to='produk')
    nama_produk = models.CharField(max_length=100)
    rettings = models.FloatField()
    harga = models.IntegerField()
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

# models.py

class Pesanan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delivered'),
        ('RETURN', 'Return'),
    ]

    nama_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nomor_hp = models.CharField(max_length=20)
    email = models.EmailField()
    alamat = models.CharField(max_length=255)
    jumlah_items = models.PositiveIntegerField()
    total_harga = models.IntegerField()
    pesanan_detail = models.TextField()  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    diterima = models.BooleanField(default=False)

    def __str__(self):
        return f"Pesanan oleh {self.nama_user} pada {self.created_at} - Status: {self.status}"
