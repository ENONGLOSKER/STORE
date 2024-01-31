from django.contrib import admin
from .models import Produk, CustomUser, Cart, CartItem
admin.site.register(Produk)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)