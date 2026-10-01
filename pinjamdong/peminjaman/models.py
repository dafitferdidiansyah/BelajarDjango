from django.db import models

class Peminjaman(models.Model):
    # Field 'id' (Nomor) otomatis dibuat oleh Django
    nama_peminjam = models.CharField(max_length=100, verbose_name="Nama Mahasiswa")
    barang_dipinjam = models.CharField(max_length=200)
    tanggal_pinjam = models.DateField(auto_now_add=True) # Otomatis terisi tanggal hari ini
    tanggal_kembali = models.DateField(null=True, blank=True) # Bisa kosong saat awal pinjam
    
    # Ini pengganti tanda tangan (Centang jika sudah kembali)
    status_dikembalikan = models.BooleanField(default=False, verbose_name="Sudah Dikembalikan?")

    def __str__(self):
        return f"{self.nama_peminjam} - {self.barang_dipinjam}"