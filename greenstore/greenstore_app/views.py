from django.shortcuts import render
from .models import Produk,CustomUser,Cart, CartItem
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import base64
import io
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.views.generic import TemplateView
import urllib.parse
from urllib.parse import quote

def datauser(request):
    data = CustomUser.objects.all()
    context = {
        'data':data
    }
    return render(request, 'user.html',context)

class SignOutView(View):

    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'success': True})

class SignInView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Username atau password salah'})
        
class SignUpView(View):
    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Register berhasil'})
        return JsonResponse({'success': False, 'errors': form.errors})

#tambah produk ke cart
class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        produk_id = self.kwargs['produk_id']
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        produk = get_object_or_404(Produk, pk=produk_id)

        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, produk=produk)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        cart_count = user_cart.items.count()

        # Simpan informasi keranjang belanja pengguna dalam session
        request.session['cart_count'] = cart_count
        request.session.save()

        return JsonResponse({'success': True, 'message': 'Item added to cart successfully', 'cart_count': cart_count})

class CartItemCountView(View):
    def get(self, request, *args, **kwargs):
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = user_cart.items.count()

        return JsonResponse({'cart_count': cart_count})

class CartView(View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = user_cart.cartitem_set.all()

        return render(request, self.template_name, {'cart_items': cart_items})

class CartSummaryView(View):
    def get(self, request, *args, **kwargs):
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = user_cart.cartitem_set.all()

        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.produk.harga * item.quantity for item in cart_items)

        return JsonResponse({'total_items': total_items, 'total_price': total_price})

class UpdateQuantityView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')
        amount = int(request.POST.get('amount')) 

        # Pastikan item ada di keranjang dan milik pengguna yang sedang login 
        cart_item = CartItem.objects.filter(cart__user=request.user, produk__id=produk_id).first()

        if cart_item:
            # Update jumlah item di keranjang
            cart_item.quantity += amount

            if cart_item.quantity < 1:
                cart_item.quantity = 1

            cart_item.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Produk tidak ditemukan di keranjang'})

class CheckoutView(View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(cart__user=request.user)
        total_items = cart_items.count()

        return render(request, self.template_name, {'cart_items': cart_items, 'total_items': total_items})

class RemoveCartItemView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')

        # Pastikan item ada di keranjang dan milik pengguna yang sedang login
        cart_item = CartItem.objects.filter(cart__user=request.user, produk__id=produk_id).first()

        if cart_item:
            cart_item.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Produk tidak ditemukan di keranjang'})

class OrderSummaryView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        nama_user = user.username
        nomor_hp = user.nomor
        email = user.email
        alamat = user.alamat

        pesanan = "\n".join(
            f"{item.produk.nama_produk} - Jumlah: {item.quantity} - Harga Satuan: Rp. {item.produk.harga}"
            for item in cart_items
        )

        jumlah_items = cart_items.count()
        total_harga = sum(item.produk.harga * item.quantity for item in cart_items)

        # Format pesan untuk WhatsApp
        whatsapp_message = (
            f"Hai admin...saya ingin pesan\n"
            f"Nama: {nama_user}\n"
            f"Alamat: {alamat}\n"
            f"Nomor: {nomor_hp}\n"
            f"Email: {email}\n"
            f"Pesanan:\n{pesanan}\n"
            "--------------------------------\n"
            f"Jumlah Item: {jumlah_items}\n"
            f"Total Bayar: Rp. {total_harga}\n"
            "--------------------------------"
        )

        # URL WhatsApp dengan parameter pesan
        whatsapp_url = f"https://wa.me/+6285239664462?text={urllib.parse.quote(whatsapp_message)}"

        return JsonResponse({'whatsapp_url': whatsapp_url, 'order_summary': {
            'nama_user': nama_user,
            'nomor_hp': nomor_hp,
            'email': email,
            'alamat': alamat,
            'jumlah_items': jumlah_items,
            'total_harga': total_harga,
        }})

# tambah produk ke katalog
class ProdukCreateView(LoginRequiredMixin, View):
    template_name = 'index.html' 

    def post(self, request, *args, **kwargs):
        img_produk = request.FILES.get('img_produk')
        nama_produk = request.POST.get('nama_produk')
        rettings = request.POST.get('rettings')
        harga = request.POST.get('harga')
        kategori = request.POST.get('kategori')

        # Validasi manual
        if not nama_produk or not rettings or not harga or not img_produk:
            return JsonResponse({'success': False, 'errors': 'Semua kolom harus diisi'})

        try:
            # Handle the image data
            img_data = img_produk.read()
            img_data = base64.b64encode(img_data).decode('utf-8')

            Produk.objects.create(
                img_produk=InMemoryUploadedFile(
                    ContentFile(base64.b64decode(img_data)),
                    None,  # field_name
                    img_produk.name,
                    'image/jpeg',  # content_type
                    len(img_data),
                    None  # charset
                ),
                nama_produk=nama_produk,
                rettings=rettings,
                harga=harga,
                kategori=kategori
            )
            return JsonResponse({'success': True, 'message': 'Data berhasil disimpan'})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

class ProdukListView(ListView):
    model = Produk
    template_name = 'index.html'
    context_object_name = 'produk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Mendapatkan semua kategori yang unik
        context['kategoris'] = Produk.objects.values('kategori').distinct()

        # Menambahkan kategori_filter ke dalam konteks untuk tetap mempertahankan filter
        context['kategori_filter'] = self.request.GET.get('kategori', '')

        return context
    
    def get_queryset(self):
        queryset = Produk.objects.all().order_by('-id')
        kategori_filter = self.request.GET.get('kategori', '')
        if kategori_filter:
            queryset = queryset.filter(kategori=kategori_filter)
        return queryset

