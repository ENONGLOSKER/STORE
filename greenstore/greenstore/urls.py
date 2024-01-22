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
from greenstore_app.views import ProdukCreateView, ProdukListView,CheckoutListView, TambahKeCartView, HapusDariCartView, UpdateJumlahItemView, SummaryView, SignUpView, SignInView, SignOutView, datauser
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', datauser, name='datauser'),
    path('checkout/', CheckoutListView.as_view(), name='checkout'),
    path('', ProdukListView.as_view(), name='index'),
    path('produk/create/', ProdukCreateView.as_view(), name='create_produk'),
    path('tambah-ke-cart/', TambahKeCartView.as_view(), name='tambah_ke_cart'),
    path('hapus-dari-cart/', HapusDariCartView.as_view(), name='hapus_dari_cart'),
    path('update-jumlah-item/', UpdateJumlahItemView.as_view(), name='update_jumlah_item'),
     path('summary/', SummaryView.as_view(), name='summary'),
    # path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

