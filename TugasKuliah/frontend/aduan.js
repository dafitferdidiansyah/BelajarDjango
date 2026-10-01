// aduan.js
document.addEventListener('DOMContentLoaded', () => {
    (() => {
        const container = document.getElementById('pengaduan-list-container');
        const apiUrl = 'http://127.0.0.1:8000/api/pengaduan/';

        // ambil token dari localStorage (DRF TokenAuth)
        const token = localStorage.getItem('authToken');
        if (!token) {
            // jika belum login, arahkan ke login
            window.location.href = 'login.html';
            return;
        }

        async function loadWargaForSelect() {
            try {
                const resp = await fetch('http://127.0.0.1:8000/api/warga/', { headers: { 'Authorization': 'Token ' + token } });
                const data = await resp.json();
                const list = Array.isArray(data) ? data : (data.results || []);
                const select = document.getElementById('pengaduan-pelapor');
                select.innerHTML = '<option value="">Pilih Pelapor</option>';
                list.forEach(w => {
                    const option = document.createElement('option');
                    option.value = w.id;
                    option.textContent = w.nama_lengkap;
                    select.appendChild(option);
                });
            } catch (err) {
                console.error('Failed to load warga for select', err);
            }
        }

        loadWargaForSelect().then(() => {
            function escapeHtml(str) {
                return String(str)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }

            function renderPengaduanCard(pengaduan, index) {
                const card = document.createElement('div');
                card.className = 'card mb-3 shadow-sm';
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title mb-2">${escapeHtml(pengaduan.judul || '-')}</h5>
                        <p class="card-text mb-1"><small class="text-muted">Status: ${escapeHtml(pengaduan.status || '-')}</small></p>
                        <p class="card-text"><small>Deskripsi: ${escapeHtml(pengaduan.deskripsi || '-')}</small></p>
                        <p class="card-text"><small>Pelapor: ${escapeHtml(pengaduan.pelapor ? pengaduan.pelapor.nama_lengkap : '-')}</small></p>
                        <div class="mt-3 d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary btn-edit">Edit</button>
                            <button class="btn btn-sm btn-outline-danger btn-delete">Hapus</button>
                        </div>
                    </div>
                `;
                card.dataset.index = index;
                card.dataset.id = pengaduan.id || '';
                return card;
            }

            function showAlert(type, message) {
                container.innerHTML = `
                    <div class="alert alert-${type}" role="alert">${escapeHtml(message)}</div>
                `;
            }

            async function loadPengaduan() {
                container.innerHTML = '<div class="d-flex justify-content-center my-5"><div class="spinner-border" role="status"><span class="visually-hidden">Memuat...</span></div></div>';
                try {
                    const resp = await fetch(apiUrl, { headers: { 'Authorization': 'Token ' + token } });
                    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

                    const data = await resp.json();
                    console.log('API response:', data);

                    // Dukung array langsung atau objek dengan properti `results`
                    const list = Array.isArray(data) ? data : (data && Array.isArray(data.results) ? data.results : null);
                    if (!list) {
                        showAlert('warning', 'Tidak ada data pengaduan atau format respons tidak dikenali. Periksa console.');
                        console.error('Unexpected API response format:', data);
                        return;
                    }

                    container.innerHTML = ''; // kosongkan spinner/mensaje

                    if (list.length === 0) {
                        showAlert('info', 'Belum ada data pengaduan. Klik "Tambah Data" untuk menambahkan.');
                        return;
                    }

                    const row = document.createElement('div');
                    row.className = 'row';

                    list.forEach((p, idx) => {
                        const col = document.createElement('div');
                        col.className = 'col-12 col-md-6';
                        col.appendChild(renderPengaduanCard(p, idx));
                        row.appendChild(col);
                    });

                    container.appendChild(row);
                    attachCardHandlers(list);
                } catch (err) {
                    showAlert('danger', 'Gagal memuat data. Pastikan server backend berjalan dan token valid.');
                    console.error('There has been a problem with your fetch operation:', err);
                }
            }

            // modal instances
            const pengaduanModalEl = document.getElementById('pengaduanModal');
            const deleteModalEl = document.getElementById('deleteModal');
            const pengaduanModal = pengaduanModalEl ? new bootstrap.Modal(pengaduanModalEl) : null;
            const deleteModal = deleteModalEl ? new bootstrap.Modal(deleteModalEl) : null;

            function attachCardHandlers(list) {
                document.querySelectorAll('.btn-edit').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const card = e.target.closest('.card');
                        const idx = parseInt(card.dataset.index, 10);
                        const data = list[idx];
                        document.getElementById('pengaduan-id').value = data.id || '';
                        document.getElementById('pengaduan-judul').value = data.judul || '';
                        document.getElementById('pengaduan-deskripsi').value = data.deskripsi || '';
                        document.getElementById('pengaduan-status').value = data.status || 'BARU';
                        document.getElementById('pengaduan-pelapor').value = data.pelapor ? data.pelapor.id : '';
                        if (pengaduanModal) pengaduanModal.show();
                    });
                });
                document.querySelectorAll('.btn-delete').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const card = e.target.closest('.card');
                        const id = card.dataset.id;
                        const confirmBtn = document.getElementById('confirm-delete-btn');
                        confirmBtn.dataset.id = id;
                        if (deleteModal) deleteModal.show();
                    });
                });
            }

            // Save handler (create / update)
            document.getElementById('pengaduan-save-btn').addEventListener('click', async () => {
                const id = document.getElementById('pengaduan-id').value;
                const judul = document.getElementById('pengaduan-judul').value.trim();
                const deskripsi = document.getElementById('pengaduan-deskripsi').value.trim();
                const status = document.getElementById('pengaduan-status').value;
                const pelapor = document.getElementById('pengaduan-pelapor').value;
                if (!judul) { alert('Judul wajib diisi'); return; }
                if (!pelapor) { alert('Pelapor wajib dipilih'); return; }

                const payload = { judul, deskripsi, status, pelapor: parseInt(pelapor) };
                try {
                    const url = id ? `${apiUrl}${id}/` : apiUrl;
                    const method = id ? 'PUT' : 'POST';
                    const resp = await fetch(url, {
                        method,
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Token ' + token },
                        body: JSON.stringify(payload)
                    });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok) { alert('Gagal menyimpan: ' + (data.detail || JSON.stringify(data))); return; }
                    if (pengaduanModal) pengaduanModal.hide();
                    await loadPengaduan();
                } catch (err) {
                    console.error('Save error', err);
                    alert('Terjadi kesalahan saat menyimpan. Lihat console.');
                }
            });

            // Delete handler
            document.getElementById('confirm-delete-btn').addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (!id) return;
                try {
                    const resp = await fetch(`${apiUrl}${id}/`, { method: 'DELETE', headers: { 'Authorization': 'Token ' + token } });
                    if (!resp.ok) {
                        const data = await resp.json().catch(() => ({}));
                        alert('Gagal menghapus: ' + (data.detail || JSON.stringify(data)));
                        return;
                    }
                    if (deleteModal) deleteModal.hide();
                    await loadPengaduan();
                } catch (err) {
                    console.error('Delete error', err);
                    alert('Terjadi kesalahan saat menghapus. Lihat console.');
                }
            });

            // Add button handler
            const addBtn = document.getElementById('add-pengaduan-btn');
            addBtn && addBtn.addEventListener('click', () => {
                document.getElementById('pengaduan-id').value = '';
                document.getElementById('pengaduan-judul').value = '';
                document.getElementById('pengaduan-deskripsi').value = '';
                document.getElementById('pengaduan-status').value = 'BARU';
                document.getElementById('pengaduan-pelapor').value = '';
                if (pengaduanModal) pengaduanModal.show();
            });

            // initial load
            loadPengaduan();
        });
    })();
});
