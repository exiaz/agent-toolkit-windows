# Verifikasi paket

Pemeriksaan pada 9 November 2026 mencakup installer, arsip distribusi, dan runtime koordinasi umum pada fixture Windows.

| Pemeriksaan | Hasil |
|---|---|
| Suite installer dan distribusi | PASSED: 9/9 tes, 28.468 detik |
| Runtime koordinasi global | PASSED: tes Node dijalankan oleh suite installer, exit 0 |
| Payload umum | PASSED: seluruh berkas dan konfigurasi memakai scope pengguna |
| Pemindaian privasi distribusi | PASSED: dokumen, manifest, dan isi teks arsip diperiksa |
| Integritas payload | PASSED: 869 berkas cocok dengan SHA-256 manifest |
| Backup, relokasi profil, dan instalasi ulang | PASSED: konfigurasi tujuan dipertahankan, instalasi kedua tanpa perubahan |
| Konflik file, hooks, dan path traversal | PASSED: perubahan berbeda dan path keluar target ditolak |
| Credits dan notices | PASSED: atribusi dan lisensi disertakan dalam arsip |

## Arsip distribusi

- Berkas: `payload.zip`
- Isi: 869 berkas
- Ukuran: 33,290,439 bytes
- SHA-256: `780025a9f6d6ebd4c0c2c9f7e4f507d248e9939cd9281452c3557c54f5b13156`

## Menjalankan pemeriksaan

```powershell
python -m unittest -v test_install.py
```

Tes memakai profil dan berkas sementara. Hasil di atas menjelaskan cakupan pemeriksaan paket, bukan sertifikasi dari penyedia aplikasi atau layanan. Setelah pemasangan, tinjau izin hooks native dan sambungkan akun layanan yang diperlukan.

Lihat [README.md](README.md) untuk pemasangan dan [CREDITS.md](CREDITS.md) untuk atribusi.
