from django.shortcuts import render
from .models import Produk,CustomUser,Cart, CartItem, Kategori
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView
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
from django.db import transaction
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

def pesanan(request):
    return render(request, 'dsh_pesanan.html')

def get_kategori_list(request):
    kategori_list = Kategori.objects.values_list('id', 'kategori')
    return JsonResponse({'kategori_list': list(kategori_list)})

class KategoriListView(View):
    def get(self, request, *args, **kwargs):
        kategori_list = Kategori.objects.values('id', 'kategori')
        return JsonResponse({'kategori_list': list(kategori_list)})
    
class ProdukAddView(View):
    def post(self, request, *args, **kwargs):
        img_produk = request.FILES.get('img_produk')
        nama_produk = request.POST.get('nama_produk')
        rettings = request.POST.get('rettings')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok')
        kategori_id = request.POST.get('kategori')

        try:
            kategori = Kategori.objects.get(id=kategori_id)
        except Kategori.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kategori tidak valid.'})

        Produk.objects.create(
            img_produk=img_produk,
            nama_produk=nama_produk,
            rettings=rettings,
            harga=harga,
            kategori=kategori,
            stok=stok
        )

        return JsonResponse({'success': True})
    
class BarangListView(ListView):
    model = Produk
    template_name = 'dsh_barang.html'  # Ganti 'nama_template_anda.html' dengan nama template yang sesuai
    context_object_name = 'produk_list'
    ordering = ['nama_produk']  # Sesuaikan dengan field yang ingin Anda gunakan sebagai urutan

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tambahkan konteks tambahan jika diperlukan
        return context
    
class DeleteProdukView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Produk, id=product_id)
        product.delete()
        return JsonResponse({'success': True})

class EditProdukView(View):
    template_name = 'dsh_barang.html'  # Sesuaikan dengan template yang Anda gunakan

    def get(self, request, produk_id):
        # Ambil data produk dari database
        produk = get_object_or_404(Produk, id=produk_id)
        # Buat formulir dengan data produk
        form = EditProdukForm(instance=produk)
        # Render template dengan formulir
        return render(request, self.template_name, {'form': form, 'produk': produk})

    def post(self, request, produk_id):
        # Ambil data produk dari database
        produk = get_object_or_404(Produk, id=produk_id)
        # Buat formulir dengan data POST dan data produk
        form = EditProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            # Simpan perubahan jika formulir valid
            form.save()
            return JsonResponse({'success': True})
        else:
            # Kirim pesan kesalahan jika formulir tidak valid
            return JsonResponse({'success': False, 'errors': form.errors})

class GetProdukDataView(View):
    def get(self, request, produk_id, *args, **kwargs):
        produk = get_object_or_404(Produk, id=produk_id)
        data = {
            'img_produk': produk.img_produk.url,
            'nama_produk': produk.nama_produk,
            'rettings': produk.rettings,
            'harga': produk.harga,
            'kategori': produk.kategori.id,  # Jika kategori adalah ForeignKey
            # Tambahkan atribut lain jika perlu
        }
        return JsonResponse(data)



# customor
class GetUserDataView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(CustomUser, id=user_id)
        data = {
            'username': user.username,
            'email': user.email,
            'nomor': user.nomor,
            'alamat': user.alamat,
        }
        return JsonResponse(data)

class CustomUserEditView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        user.username = request.POST.get('edit_username')
        user.email = request.POST.get('edit_email')
        user.nomor = request.POST.get('edit_nomor')
        user.alamat = request.POST.get('edit_alamat')

        # Ubah password hanya jika diisi
        new_password = request.POST.get('edit_password')
        if new_password:
            user.set_password(new_password)

        user.save()

        return JsonResponse({'success': True})

class CustomUserDeleteView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        return JsonResponse({'success': True})
    
class CustomUserListView(ListView):
    model = CustomUser
    template_name = 'dsh_customor.html'
    context_object_name = 'custom_users'


# AUTH
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

#USER PAGE CART AND SUMMARY ORDER
class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        produk_id = self.kwargs['produk_id']
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        produk = get_object_or_404(Produk, pk=produk_id)

        # Pemeriksaan stok
        if produk.stok > 0:
            cart_item, created = CartItem.objects.get_or_create(cart=user_cart, produk=produk)
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            # Kurangi stok
            produk.stok -= 1
            produk.save()

            cart_count = user_cart.items.count()

            # Simpan informasi keranjang belanja pengguna dalam session
            request.session['cart_count'] = cart_count
            request.session.save()

            return JsonResponse({'success': True, 'message': 'Item added to cart successfully', 'cart_count': cart_count})
        else:
            return JsonResponse({'success': False, 'message': 'Stok produk tidak mencukupi'})

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

            # Perbarui stok produk
            produk = get_object_or_404(Produk, id=produk_id)
            produk.stok -= amount
            produk.save()

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

        with transaction.atomic():
            # Pastikan item ada di keranjang dan milik pengguna yang sedang login
            cart_item = CartItem.objects.filter(cart__user=request.user, produk__id=produk_id).first()

            if cart_item:
                # Simpan jumlah item sebelum dihapus
                removed_quantity = cart_item.quantity

                cart_item.delete()

                # Kembalikan stok produk
                produk = get_object_or_404(Produk, id=produk_id)
                produk.stok += removed_quantity
                produk.save()

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
            f"Hallo admin, Saya ingin melakukan pemesanan produk. Detail pesanannya:\n"
            f"Nama: {nama_user}\n"
            f"Alamat: {alamat}\n"
            f"Nomor: {nomor_hp}\n"
            f"Email: {email}\n"
            "---------------------------------------------\n"
            f"Pesanan:\n{pesanan}\n"
            "---------------------------------------------\n"
            f"Jumlah Item: {jumlah_items}\n"
            f"Total Bayar: Rp. {total_harga}\n"
            "---------------------------------------------\n"
            "Mohon konfirmasi mengenai informasi pembayaran.Terima kasih!\n\n\n"
            
            f"Salam Customor,\n {nama_user}"
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



# user 
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

def kategori(request):
    data = Kategori.objects.all()

    context = {
        'kategoris': data,
    }
    return render(request, 'dsh_kategori.html',context)


def datauser(request):
    data = CustomUser.objects.all()
    context = {
        'data':data
    }
    return render(request, 'dashboard.html',context)