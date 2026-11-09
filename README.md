# ModifyGameBrickBreaker_119

**BRICK BREAKER – ARCADE EDITION**

Tugas Pemrograman Multiplatform – Topic 9: Implementasi OOP di GUI Programming

- **Nama:** Fazilatun Nisa Muslimah
- **NIM:** 20250140119
- **Kode asli:** [Studytonight – Brick Breaker Game using Tkinter](https://www.studytonight.com/tkinter/brick-breaker-game-using-tkinter-python-project)

## Cara menjalankan

```bash
pip install pygame-ce      # opsional, untuk musik latar + efek suara
python brick_breaker.py
```

Tanpa `pygame-ce` game tetap jalan. Di Windows efek suara tetap bunyi lewat `winsound`, tapi tanpa musik latar.

## Kontrol

| Tombol | Fungsi |
|---|---|
| Mouse / panah kiri-kanan | Gerakkan paddle |
| Spasi / klik | Mulai, lempar bola, main lagi |
| P | Pause / lanjut |
| M | Musik on / off |

## Daftar modifikasi

| No | Modifikasi | Keterangan |
|---|---|---|
| 1 | Tema neon arcade | Latar grid retro, bintang bergerak, warna neon, teks berbayang |
| 2 | Title screen | Judul berganti warna pelangi, teks berkedip, high score, petunjuk kontrol |
| 3 | Efek suara chiptune | Suara paddle, dinding, bata retak, bata pecah, power-up, nyawa hilang, level clear, game over |
| 4 | Musik latar | Lagu chiptune 8 bar yang diputar berulang (bisa dimatikan dengan M) |
| 5 | Partikel ledakan | Bata pecah menyebar jadi partikel sesuai warnanya + teks skor melayang |
| 6 | Screen shake | Layar bergetar saat bata pecah dan saat nyawa hilang |
| 7 | Jejak bola | Bola meninggalkan ekor seperti komet |
| 8 | Combo | Pecahkan bata berturut-turut tanpa menyentuh paddle, skor dikali combo |
| 9 | Power-up | `W` paddle lebar, `S` bola lambat, `+` nyawa tambahan |
| 10 | 4 desain level + level acak | Tiap level punya pola bata berbeda, setelah level 4 dibuat acak dan makin sulit |
| 11 | Bata 1–3 hit | Warna bata berubah tiap kali kena |
| 12 | Kecepatan bertambah | Bola makin cepat tiap memantul dan tiap naik level |
| 13 | Pantulan bersudut | Arah bola tergantung titik kena di paddle |
| 14 | High score tersimpan | Disimpan di `highscore.json`, tidak hilang saat game ditutup |
| 15 | Pause & musik on/off | Tombol P dan M |
| 16 | Gerak paddle halus | Tahan tombol panah untuk gerak terus, atau pakai mouse |

## Struktur file

| File | Isi |
|---|---|
| `brick_breaker.py` | Class `Ball`, `Paddle`, `Brick`, dan `Game` (loop utama ~60 FPS) |
| `game_object.py` | Class induk `GameObject` |
| `powerups.py` | Class `PowerUp` (turunan `GameObject`) |
| `effects.py` | Class `Starfield`, `Particles`, `Shake` |
| `sound.py` | Class `Sound`, pembuat efek suara & musik chiptune |
| `highscore.py` | Simpan / baca high score |
| `settings.py` | Warna, ukuran, dan pola level |

## Konsep OOP yang dipakai

- **Inheritance:** `Ball`, `Paddle`, `Brick`, `PowerUp` mewarisi `GameObject`. `Game` mewarisi `tk.Frame`.
- **Encapsulation:** tiap class mengurus datanya sendiri (misal `Brick.hit()` mengatur sisa hit dan warnanya).
- **Polymorphism:** `Paddle.move()` meng-override `GameObject.move()` supaya paddle tidak keluar layar.
- **Composition:** `Game` memakai objek `Sound`, `Starfield`, `Particles`, dan `Shake`.
