from django.urls import path
from . import views

urlpatterns = [
    path('', views.PeminjamanListView.as_view(), name='daftar_pinjam'),
    path('tambah/', views.PeminjamanCreateView.as_view(), name='tambah_pinjam'),
    path('edit/<int:pk>/', views.PeminjamanUpdateView.as_view(), name='edit_pinjam'),
    path('hapus/<int:pk>/', views.PeminjamanDeleteView.as_view(), name='hapus_pinjam'),
]