# ModifyGameBrickBreaker_119

Tugas Pemrograman Multiplatform – Topic 9: Implementasi OOP di GUI Programming

- **Nama:** Fazilatun Nisa Muslimah
- **NIM:** 20250140119
- **Kode asli:** [Studytonight – Brick Breaker Game using Tkinter](https://www.studytonight.com/tkinter/brick-breaker-game-using-tkinter-python-project)

## Cara menjalankan

```bash
python brick_breaker.py
```

Butuh Python 3 dengan Tkinter (sudah bawaan Python di Windows).

## Kontrol

| Tombol | Fungsi |
|---|---|
| Mouse / panah kiri-kanan | Gerakkan paddle |
| Spasi | Mulai / main lagi setelah game over |
| P | Pause / lanjut |

## Daftar modifikasi

| No | Modifikasi | Keterangan |
|---|---|---|
| 1 | Sistem skor | Bata 1 hit = 10, 2 hit = 20, 3 hit = 30 poin |
| 2 | Level bertingkat | Semua bata habis → naik level, bonus 100 × level |
| 3 | Tingkat kesulitan | Tiap level: baris bata bertambah, bata keras lebih banyak, bola lebih cepat |
| 4 | High score | Skor tertinggi disimpan selama program jalan |
| 5 | Pause | Tekan P untuk berhenti sementara |
| 6 | Restart | Spasi setelah game over untuk main lagi tanpa menutup program |
| 7 | Kontrol mouse | Paddle mengikuti posisi mouse |
| 8 | Pantulan bersudut | Arah bola tergantung titik kena di paddle (pinggir = miring tajam) |
| 9 | HUD baru | Nyawa berbentuk hati, skor, high score, dan level di bagian atas |
| 10 | Tema gelap | Warna latar, paddle, dan bata diganti |
| 11 | Perbaikan bug | Bola tidak lagi "nyangkut" di dinding, paddle tidak bisa keluar layar |

## Struktur OOP

- `GameObject` – class induk (posisi, gerak, hapus)
- `Ball`, `Paddle`, `Brick` – turunan `GameObject` (inheritance)
- `Game` – turunan `tk.Frame`, mengatur level, skor, nyawa, dan game loop
