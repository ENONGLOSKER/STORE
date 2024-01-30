"""
URL configuration for greenstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from greenstore_app.views import ProdukListView, SignUpView, SignInView, SignOutView, AddToCartView, CartItemCountView, CartView, CartSummaryView, UpdateQuantityView, CheckoutView, RemoveCartItemView, OrderSummaryView,CustomUserListView,CustomUserDeleteView,CustomUserEditView,GetUserDataView, datauser,kategori, pesanan, BarangListView,DeleteProdukView, get_kategori_list, ProdukAddView, KategoriListView,EditProdukView, GetProdukDataView,KategoriListView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', datauser, name='dashboard'),
    path('kategori/', kategori, name='kategori'),
    path('pesanan/', pesanan, name='pesanan'),

    # kategori
    path('kategori-list/', get_kategori_list, name='kategori_list'),
    path('produk/add/', ProdukAddView.as_view(), name='produk_add'),
    path('get-kategori-list/', KategoriListView.as_view(), name='get_kategori_list'),
    # produk
    path('produk-list/', BarangListView.as_view(), name='barang'),
    path('delete-produk/<int:product_id>/', DeleteProdukView.as_view(), name='delete_produk'),
    path('get_produk_data/<int:produk_id>/', GetProdukDataView.as_view(), name='get_produk_data'),
    path('edit_produk/<int:produk_id>/', EditProdukView.as_view(), name='edit_produk'),

    # custumor
    path('customor/', CustomUserListView.as_view(), name='customor'),
    path('delete_user/<int:user_id>/', CustomUserDeleteView.as_view(), name='delete_user'),
    path('edit_user/<int:user_id>/', CustomUserEditView.as_view(), name='edit_user'),
    path('get_user_data/<int:user_id>/', GetUserDataView.as_view(), name='get_user_data'),

    # untuk authentikasi user
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),

    # untuk tampilan user 
    path('add_to_cart/<int:produk_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart_item_count/', CartItemCountView.as_view(), name='cart_item_count'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart_summary/', CartSummaryView.as_view(), name='cart_summary'),
    path('update_quantity/', UpdateQuantityView.as_view(), name='update_quantity'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('remove_cart_item/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    # path('get_order_summary/', get_order_summary, name='get_order_summary'),
    path('get_order_summary/', OrderSummaryView.as_view(), name='get_order_summary'),
    path('send_order_whatsapp/', OrderSummaryView.as_view(), name='send_order_whatsapp'),

    # product
    path('', ProdukListView.as_view(), name='index'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

