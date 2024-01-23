from django.contrib import admin
from .models import Produk, CustomUser, Cart, CartItem
# Register your models here.
admin.site.register(Produk)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)