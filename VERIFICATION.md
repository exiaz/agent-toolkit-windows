# Verifikasi paket

Pemeriksaan pada 9 November 2026 mencakup installer, arsip distribusi, dan runtime koordinasi umum pada fixture Windows.

| Pemeriksaan | Hasil |
|---|---|
| Suite installer dan distribusi | PASSED: 10/10 tes, 43.387 detik |
| Runtime koordinasi global | PASSED: tes Node dijalankan oleh suite installer, exit 0 |
| Payload umum | PASSED: seluruh berkas dan konfigurasi memakai scope pengguna |
| Pemindaian privasi distribusi | PASSED: dokumen, manifest, dan isi teks arsip diperiksa |
| Integritas payload | PASSED: 1216 berkas cocok dengan SHA-256 manifest |
| Backup, relokasi profil, dan instalasi ulang | PASSED: konfigurasi tujuan dipertahankan, instalasi kedua tanpa perubahan |
| Konflik file, hooks, dan path traversal | PASSED: perubahan berbeda dan path keluar target ditolak |
| Koleksi Awesome DESIGN.md | PASSED: 84 referensi, integritas upstream, salinan skill Claude, dan lisensi VoltAgent |
| Credits dan notices | PASSED: atribusi dan lisensi disertakan dalam arsip |

## Arsip distribusi

- Berkas: `payload.zip`
- Isi: 1216 berkas
- Ukuran: 34,897,074 bytes
- SHA-256: `7376fd84ea1867c5865a53c1b1e423547f23ae26d2bce4160bb9ebdc605218cb`

## Menjalankan pemeriksaan

```powershell
python -m unittest -v test_install.py
```

Tes memakai profil dan berkas sementara. Hasil di atas menjelaskan cakupan pemeriksaan paket, bukan sertifikasi dari penyedia aplikasi atau layanan. Setelah pemasangan, tinjau izin hooks native dan sambungkan akun layanan yang diperlukan.

Lihat [README.md](README.md) untuk pemasangan dan [CREDITS.md](CREDITS.md) untuk atribusi.
