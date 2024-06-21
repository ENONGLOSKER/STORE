from django.shortcuts import render
from .models import Produk,CustomUser,Cart, CartItem, Pesanan
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
import urllib.parse
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.db.models import Q
import locale

class UpdateRettingsView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id') # Menggunakan produk_id
        try:
            produk = Produk.objects.get(id=produk_id)
            produk.rettings += 1  # Tambah rettings dengan 1
            produk.save()
            return JsonResponse({'success': True})
        except Produk.DoesNotExist:
            return JsonResponse({'error': 'Produk tidak ditemukan'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# USER PESANAN
class PesananListView(ListView):
    model = Pesanan
    template_name = 'status.html'
    context_object_name = 'pesanan'

    def get_queryset(self):
        return Pesanan.objects.filter(nama_user=self.request.user).order_by('-id')

class PesananDiterimaView(View):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')  
        try:
            order = Pesanan.objects.get(id=order_id)
            order.diterima = True  
            order.save()
            return JsonResponse({'success': True})
        except Pesanan.DoesNotExist:
            return JsonResponse({'error': 'Pesanan tidak ditemukan'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class PesananBatalView(View):
    def post(self, request, *args, **kwargs):
        pesanan_id = request.POST.get('pesanan_id')
        try:
            pesanan = Pesanan.objects.get(id=pesanan_id)
            pesanan.status = 'RETURN' 
            pesanan.save()
            return JsonResponse({'success': True})
        except Pesanan.DoesNotExist:
            return JsonResponse({'error': 'Pesanan tidak ditemukan'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# USER PAGE CART 
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

class OrderSummaryView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            return JsonResponse({'error': 'Keranjang kosong.'}, status=400)

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

        # Set locale ke 'id_ID' untuk menggunakan format mata uang Indonesia
        locale.setlocale(locale.LC_ALL, 'id_ID')

        try:
            whatsapp_message = f"Hallo admin, Saya ingin melakukan pemesanan\n" \
                                f"Nama: {nama_user}\n" \
                                f"Alamat: {alamat}\n" \
                                f"Nomor: {nomor_hp}\n" \
                                f"Email: {email}\n" \
                                "---------------------------------------------\n" \
                                f"Detail Pesanan:\n{pesanan}\n" \
                                "---------------------------------------------\n" \
                                f"Jumlah Item: {jumlah_items}\n" \
                                f"*Total Bayar:* *Rp. {locale.format_string('%d', total_harga, grouping=True)}*\n" \
                                "---------------------------------------------\n" \
                                "Mohon konfirmasi mengenai informasi pembayaran. Terima kasih!\n\n\n" \
                                f"Salam Customer,\n {nama_user}"

            admin_whatsapp_number = "+6281913428083"
            whatsapp_url = f"https://wa.me/{admin_whatsapp_number}?text={urllib.parse.quote(whatsapp_message)}"
            
            return JsonResponse({'whatsapp_url': whatsapp_url, 'order_summary': {
                'nama_user': nama_user,
                'nomor_hp': nomor_hp,
                'email': email,
                'alamat': alamat,
                'jumlah_items': jumlah_items,
                'total_harga': total_harga,
            }})
        except Exception as e:
            return JsonResponse({'error': f'Terjadi kesalahan saat membuat pesanan: {str(e)}'}, status=500)

class SaveOrderView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            return JsonResponse({'error': 'Keranjang kosong.'}, status=400)

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

        try:
            with transaction.atomic():
                # Simpan pesanan ke dalam model Pesanan
                order_summary_user = Pesanan.objects.create(
                    nama_user=user,
                    nomor_hp=nomor_hp,
                    email=email,
                    alamat=alamat,
                    jumlah_items=jumlah_items,
                    total_harga=total_harga,
                    pesanan_detail=pesanan
                )

                cart_items.delete()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': f'Terjadi kesalahan saat membuat pesanan: {str(e)}'}, status=500)

class ProdukListView(ListView):
    model = Produk
    template_name = 'index.html'
    context_object_name = 'produk'

    def get_queryset(self):
        queryset = Produk.objects.all().order_by('-id')
        filter_type = self.request.GET.get('filter_type', '')
        
        if filter_type == 'termurah':
            queryset = queryset.order_by('harga')
        elif filter_type == 'termahal':
            queryset = queryset.order_by('-harga')

        return queryset

class RemoveCartItemView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')

        with transaction.atomic():
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
            
# ADMIN DASHBOARD
class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        data = CustomUser.objects.all()
        count_customor = CustomUser.objects.all().count()
        count_produk = Produk.objects.all().count()
        count_pesanan_trm = Pesanan.objects.filter(status='DELIVERED').count()
        count_pesanan_btl = Pesanan.objects.filter(status='RETURN').count()
        context = {
            'data': data,
            'count_customor': count_customor,
            'count_produk': count_produk,
            'count_pesanaTRM': count_pesanan_trm,
            'count_pesanaBTL': count_pesanan_btl,
        }
        return render(request, self.template_name, context)

# ADMIN PESANAN
class OrderListView(View):
    template_name = 'dsh_pesanan.html'

    def get(self, request, *args, **kwargs):
        # Ambil parameter filter dari URL
        customer_id = request.GET.get('customer')
        date_filter = request.GET.get('date')
        status_filter = request.GET.get('status')

        # Ambil data pelanggan untuk opsi filter
        customers = CustomUser.objects.all()

        # Ambil semua opsi status yang ada
        status_options = Pesanan.STATUS_CHOICES

        # Buat query awal
        orders = Pesanan.objects.all().order_by('-id')

        # Filter berdasarkan pelanggan
        if customer_id:
            orders = orders.filter(nama_user_id=customer_id)

        # Filter berdasarkan tanggal
        if date_filter == 'today':
            # Filter untuk hari ini
            today = datetime.now().date()
            orders = orders.filter(created_at__date=today)
        elif date_filter == 'week':
            # Filter untuk seminggu terakhir
            week_ago = datetime.now().date() - timedelta(days=7)
            orders = orders.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            # Filter untuk sebulan terakhir
            month_ago = datetime.now().date() - timedelta(days=30)
            orders = orders.filter(created_at__date__gte=month_ago)

        # Filter berdasarkan status
        if status_filter:
            orders = orders.filter(status=status_filter)


        count_pandding = Pesanan.objects.filter(status='PENDING').count()
        count_progres = Pesanan.objects.filter(status='PROGRES').count()
        count_delivered = Pesanan.objects.filter(status='DELIVERED').count()
        count_return = Pesanan.objects.filter(status='RETURN').count()

        context = {
            'orders': orders,
            'customers': customers,
            'status_options': status_options,
            'count_pandding': count_pandding,
            'count_progres': count_progres,
            'count_delivered': count_delivered,
            'count_return': count_return
        }
        return render(request, self.template_name, context)
    
class UpdateOrderStatusView(View):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        try:
            order = Pesanan.objects.get(id=order_id)
            order.status = new_status
            order.save()
            return JsonResponse({'success': True})
        except Pesanan.DoesNotExist:
            return JsonResponse({'error': 'Pesanan tidak ditemukan'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
       
# ADMIN PRODUK
class AddProdukView(View):
    def post(self, request, *args, **kwargs):
        img_produk = request.FILES.get('img_produk')
        nama_produk = request.POST.get('nama_produk')
        rettings = request.POST.get('rettings')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok')

        produk_baru = Produk(
            img_produk=img_produk,
            nama_produk=nama_produk,
            rettings=rettings,
            harga=harga,
            stok=stok
        )
        produk_baru.save()

        return JsonResponse({'success': True})

class BarangListView(ListView):
    model = Produk
    template_name = 'dsh_barang.html'  
    context_object_name = 'produk_list'
    ordering = ['-id'] 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BarangListView(ListView):
    model = Produk
    template_name = 'dsh_barang.html'  
    context_object_name = 'produk_list'
    ordering = ['-id'] 
    paginate_by = 6
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Produk.objects.filter(nama_produk__icontains=query).order_by('-id')
        return Produk.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    
class DeleteProdukView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Produk, id=product_id)
        product.delete()
        return JsonResponse({'success': True})

class EditProdukView(View):
    template_name = 'dsh_barang.html'  

    def get(self, request, *args, **kwargs):
        produk_id = kwargs.get('produk_id')
        produk = get_object_or_404(Produk, id=produk_id)
        data = {
            'nama_produk': produk.nama_produk,
            'rettings': produk.rettings,
            'harga': produk.harga,
            'stok': produk.stok,
            'gambar': produk.img_produk.url,
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        produk_id = kwargs.get('produk_id')
        produk = get_object_or_404(Produk, id=produk_id)

        produk.img_produk = request.FILES.get('img_produk', produk.img_produk)
        produk.nama_produk = request.POST.get('nama_produk', produk.nama_produk)
        produk.rettings = request.POST.get('rettings', produk.rettings)
        produk.harga = request.POST.get('harga', produk.harga)
        produk.stok = request.POST.get('stok', produk.stok)

        produk.save()

        return JsonResponse({'success': True, 'img_produk': produk.img_produk.url})
    
# ADMIN CUSTOMOR
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
    ordering = ['-id']
    paginate_by = 10
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return CustomUser.objects.filter(username__icontains=query).order_by('-id')
        return CustomUser.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

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
            is_superuser = user.is_superuser
            return JsonResponse({'success': True, 'is_superuser':user.is_superuser})
        else:
            return JsonResponse({'success': False, 'message': 'Username atau password salah'})
        
class SignUpView(View):
    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Register berhasil'})
        return JsonResponse({'success': False, 'errors': form.errors})
