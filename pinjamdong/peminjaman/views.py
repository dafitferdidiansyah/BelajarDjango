from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin # Tambahkan ini
from .models import Peminjaman

# Tambahkan LoginRequiredMixin di parameter pertama pada setiap class
class PeminjamanListView(LoginRequiredMixin, ListView):
    model = Peminjaman
    template_name = 'peminjaman/daftar_pinjam.html'
    context_object_name = 'data_pinjam'
    ordering = ['-tanggal_pinjam']

class PeminjamanCreateView(LoginRequiredMixin, CreateView):
    model = Peminjaman
    fields = ['nama_peminjam', 'barang_dipinjam', 'status_dikembalikan', 'tanggal_kembali']
    template_name = 'peminjaman/form_pinjam.html'
    success_url = reverse_lazy('daftar_pinjam')

class PeminjamanUpdateView(LoginRequiredMixin, UpdateView):
    model = Peminjaman
    fields = ['nama_peminjam', 'barang_dipinjam', 'status_dikembalikan', 'tanggal_kembali']
    template_name = 'peminjaman/form_pinjam.html'
    success_url = reverse_lazy('daftar_pinjam')

class PeminjamanDeleteView(LoginRequiredMixin, DeleteView):
    model = Peminjaman
    template_name = 'peminjaman/konfirmasi_hapus.html'
    success_url = reverse_lazy('daftar_pinjam')