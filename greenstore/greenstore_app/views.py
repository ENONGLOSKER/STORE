from django.shortcuts import render
from .models import Produk,CustomUser
# views.py
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import base64
import io
# views.py
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# menampilkan semua user

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


class SummaryView(View):
    def get(self, request, *args, **kwargs):
        if 'cart' in request.session:
            jumlah_items = sum(item['jumlah'] for item in request.session['cart'].values())
            total_harga = sum(item['jumlah'] * item['harga'] for item in request.session['cart'].values())
            return JsonResponse({'success': True, 'jumlah_items': jumlah_items, 'total_harga': total_harga})
        return JsonResponse({'success': False})

class UpdateJumlahItemView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')
        tindakan = request.POST.get('tindakan')

        if 'cart' in request.session and produk_id in request.session['cart']:
            if tindakan == "tambah":
                request.session['cart'][produk_id]['jumlah'] += 1
            elif tindakan == "kurang" and request.session['cart'][produk_id]['jumlah'] > 1:
                request.session['cart'][produk_id]['jumlah'] -= 1

            request.session.save()
            return JsonResponse({'success': True, 'jumlah_item': request.session['cart'][produk_id]['jumlah']})

        return JsonResponse({'success': False})

class HapusDariCartView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')

        if 'cart' in request.session and produk_id in request.session['cart']:
            del request.session['cart'][produk_id]
            request.session.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})

class TambahKeCartView(View):
    def post(self, request, *args, **kwargs):
        produk_id = request.POST.get('produk_id')
        produk = get_object_or_404(Produk, id=produk_id)

        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session['cart']
        if produk_id in cart:
            cart[produk_id]['jumlah'] += 1
        else:
            cart[produk_id] = {
                'nama_produk': produk.nama_produk,
                'kategori': produk.kategori,
                'harga': produk.harga,
                'rettings': produk.rettings,
                'jumlah': 1,
            }

        request.session.save()
        jumlah_item = sum(item['jumlah'] for item in cart.values())
        
        return JsonResponse({'success': True, 'jumlah_item': jumlah_item})

class ProdukCreateView(View):
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
    
class CheckoutListView(ListView):
    model = Produk
    template_name = 'checkout.html'
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
