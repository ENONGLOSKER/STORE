from django.shortcuts import render
from .models import Produk
# views.py
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

class ProdukCreateView(View):
    template_name = 'index.html' 

    def post(self, request, *args, **kwargs):
        nama_produk = request.POST.get('nama_produk')
        rettings = request.POST.get('rettings')
        harga = request.POST.get('harga')
        kategori = request.POST.get('kategori')

        # Validasi manual
        if not nama_produk or not rettings or not harga:
            return JsonResponse({'success': False, 'errors': 'Semua kolom harus diisi'})

        try:
            Produk.objects.create(nama_produk=nama_produk, rettings=rettings, harga=harga, kategori=kategori)
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
