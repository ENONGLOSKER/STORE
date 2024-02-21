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
from django.conf import settings
from django.conf.urls.static import static

from greenstore_app.views import SignUpView, SignInView, SignOutView, AddToCartView, CartItemCountView, CartView, CartSummaryView, UpdateQuantityView, CheckoutView, RemoveCartItemView,CustomUserListView,CustomUserDeleteView,CustomUserEditView,GetUserDataView, DashboardView, OrderListView, BarangListView,DeleteProdukView, AddProdukView, EditProdukView, ProdukListView, SaveOrderView, OrderSummaryView, UpdateOrderStatusView,PesananListView, PesananDiterimaView,PesananBatalView, UpdateRettingsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('status/', PesananListView.as_view(), name='status'),
    path('pesanan/diterima/', PesananDiterimaView.as_view(), name='pesanan_diterima'),
    path('pesanan/batal/', PesananBatalView.as_view(), name='pesanan_batal'),
    path('pesanan/', OrderListView.as_view(), name='pesanan'),
    path('update_order_status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('barang/update-rettings/', UpdateRettingsView.as_view(), name='update_rettings'),

    # produk
    path('', ProdukListView.as_view(), name='index'),
    path('produk-list/', BarangListView.as_view(), name='barang'),
    path('barang/search/', BarangListView.as_view(), name='barang_search'),
    path('tambah-produk/', AddProdukView.as_view(), name='tambah_produk'),
    path('delete-produk/<int:product_id>/', DeleteProdukView.as_view(), name='delete_produk'),
    path('edit-produk/<int:produk_id>/', EditProdukView.as_view(), name='edit_produk'),

    # custumor
    path('customor/', CustomUserListView.as_view(), name='customor'),
    path('customor/search/', CustomUserListView.as_view(), name='customor_search'),
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
    path('get_order_summary/', OrderSummaryView.as_view(), name='get_order_summary'),
    path('send_order_whatsapp/', OrderSummaryView.as_view(), name='send_order_whatsapp'),
    path('save_order/', SaveOrderView.as_view(), name='save_order')   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

