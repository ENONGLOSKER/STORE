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
from greenstore_app.views import ProdukCreateView, ProdukListView, SignUpView, SignInView, SignOutView, datauser , AddToCartView, CartItemCountView, CartView, CartSummaryView, UpdateQuantityView, CheckoutView, RemoveCartItemView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', datauser, name='datauser'),
    # product
    path('', ProdukListView.as_view(), name='index'),
    path('produk/create/', ProdukCreateView.as_view(), name='create_produk'),
    # cart
    path('add_to_cart/<int:produk_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart_item_count/', CartItemCountView.as_view(), name='cart_item_count'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart_summary/', CartSummaryView.as_view(), name='cart_summary'),
    path('update_quantity/', UpdateQuantityView.as_view(), name='update_quantity'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('remove_cart_item/', RemoveCartItemView.as_view(), name='remove_cart_item'),

    # auth
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

