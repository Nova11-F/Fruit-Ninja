<div align="center">

## 🍉 FRUIT NINJA CV

### *Game Tebas Buah dengan Gerakan Jari*

[![Python](https://img.shields.io/badge/Python-3.8--3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-0097A7?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![License](https://img.shields.io/badge/License-Educational-blue?style=for-the-badge)]()

Game interaktif ala *Fruit Ninja* yang dikendalikan sepenuhnya oleh **gerakan jari telunjuk** di depan webcam, tanpa mouse, keyboard, maupun controller tambahan.

</div>


# 📖 Tentang Proyek

**Fruit Ninja CV** merupakan game berbasis *Computer Vision* yang dibangun menggunakan **Python**, **OpenCV**, dan **MediaPipe Hands**. Kamera menangkap gerakan tangan pemain, lalu ujung jari telunjuk dilacak secara *real-time* dan berperan sebagai "pedang" untuk menebas buah yang beterbangan di layar.

Game ini memungkinkan pengguna untuk:

- 🖐️ Mengendalikan permainan hanya dengan jari telunjuk melalui webcam
- 🍎 Menebas berbagai jenis buah dan mengumpulkan skor
- 💣 Menghindari bom yang akan mengurangi skor
- 🔥 Mendapatkan bonus combo dengan menebas beberapa buah sekaligus dalam satu tebasan
- 🏆 Memecahkan rekor skor tertinggi selama sesi permainan

Proyek ini dibuat sebagai media pembelajaran dalam menerapkan konsep **Hand Tracking**, **Computer Vision**, **Game Loop**, **Object-Oriented Programming**, serta **Deteksi Tabrakan (Collision Detection)**.


## ✨ Fitur Utama

- **🖐️ Pelacakan Jari Telunjuk**:
  - Menggunakan **MediaPipe Hands** untuk mendeteksi satu tangan dan melacak titik *INDEX_FINGER_TIP* (landmark ke-8).
  - Gambar kamera otomatis dicerminkan (*mirror*) dan sedikit diredupkan agar objek game terlihat jelas.

- **⚔️ Sistem Tebasan**:
  - Tebasan hanya dihitung jika kecepatan jari melebihi batas minimum (`SLICE_SPEED`), sehingga gerakan pelan tidak memotong buah.
  - Deteksi tabrakan menggunakan perhitungan **segmen garis terhadap lingkaran**, sehingga tebasan cepat tetap terdeteksi akurat.
  - Jejak tebasan bercahaya mengikuti pergerakan jari.

- **🍓 Buah & Bom**:
  - Lima jenis buah dengan warna dan ukuran berbeda: **apel**, **jeruk**, **semangka**, **lemon**, dan **anggur**.
  - **Bom** (hitam bertanda `X`) muncul secara acak dengan peluang 18%.
  - Setiap lemparan terdiri dari 1 hingga 3 objek, diarahkan ke tengah layar dengan fisika gravitasi.

- **✨ Efek Visual**:
  - Buah terbelah menjadi dua potongan saat ditebas.
  - Percikan partikel berwarna sesuai buah.
  - Layar berkedip merah ketika menebas bom.

- **⏱️ Alur Permainan**:
  - Hitung mundur **3 detik** sebelum permainan dimulai.
  - Durasi permainan **60 detik** dengan bar waktu di bagian atas layar.
  - Timer berubah merah pada **10 detik terakhir**.
  - Buah yang terlewat tidak mengurangi skor, game tetap berjalan.

- **📊 Sistem Skor**:
  - Skor saat ini dan skor terbaik tampil di layar.
  - Pesan **REKOR BARU!** muncul ketika skor tertinggi terpecahkan.
  - Penghitung **FPS** ditampilkan di pojok kanan atas.

- **📷 Deteksi Kamera Otomatis**:
  - Mencari kamera yang benar-benar bisa mengirim gambar (index 0–3).
  - Di Windows, mencoba backend `DSHOW`, `MSMF`, lalu `ANY` secara berurutan.


## 🎮 Aturan Permainan

| Objek | Efek pada Skor | Keterangan |
| :--- | :--- | :--- |
| **Buah** 🍎 | `+10` | Setiap buah yang berhasil ditebas |
| **Combo** 🔥 | `+5 × jumlah buah` | Bonus jika ≥ 2 buah tertebas dalam satu tebasan |
| **Bom** 💣 | `-20` | Skor tidak akan kurang dari `0`, combo direset |
| **Buah terlewat** 🍋 | `0` | Tidak ada pengurangan skor |


## ⌨️ Kontrol

| Input | Fungsi |
| :--- | :--- |
| **Jari telunjuk** | Menebas buah di layar |
| `R` | Main ulang |
| `Q` / `ESC` | Keluar dari game |


## 🛠️ Teknologi yang Digunakan

- **Python**: Bahasa pemrograman utama dengan pendekatan *object-oriented*.
- **OpenCV (`opencv-python`)**: Menangkap gambar webcam, menggambar objek game, teks, dan efek visual.
- **MediaPipe (`0.10.14`)**: Deteksi dan pelacakan landmark tangan secara real-time.
- **NumPy**: Pengolahan array gambar untuk efek peredupan layar.


## 📁 Struktur Proyek

```text
.
├── fruit_ninja.py    # Seluruh logika game, deteksi tangan, dan tampilan
└── README.md         # Dokumentasi proyek
```


## 💻 Cara Menjalankan Proyek

### Prasyarat

- **Python 3.8 – 3.12** (disarankan, sesuai dukungan MediaPipe 0.10.14)
- **Webcam** yang berfungsi
- Ruangan dengan **pencahayaan yang cukup** agar tangan terdeteksi dengan baik

### Instalasi

```bash
# 1. Clone repositori
git clone https://github.com/<username>/<nama-repositori>.git
cd <nama-repositori>

# 2. (Opsional) Buat virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Instal dependensi
pip install opencv-python mediapipe==0.10.14 numpy
```

### Menjalankan Game

```bash
python fruit_ninja.py
```

Jendela game bernama **Fruit Ninja CV** akan terbuka. Arahkan jari telunjuk ke kamera dan tunggu hitung mundur selesai.


## ⚙️ Konfigurasi

Tingkat kesulitan dan perilaku game dapat disesuaikan melalui konstanta di bagian atas file `fruit_ninja.py`:

| Konstanta | Nilai Default | Fungsi |
| :--- | :---: | :--- |
| `WIDTH`, `HEIGHT` | `1280`, `720` | Resolusi jendela dan kamera |
| `GRAVITY` | `0.45` | Gaya gravitasi pada objek |
| `SPAWN_INTERVAL` | `0.9` | Jeda antar lemparan dalam detik (makin kecil makin sulit) |
| `SLICE_SPEED` | `25` | Kecepatan minimum jari (piksel/frame) agar dianggap tebasan |
| `TRAIL_LENGTH` | `12` | Panjang jejak tebasan |
| `ROUND_TIME` | `60` | Durasi permainan dalam detik |
| `COUNTDOWN` | `3` | Hitung mundur sebelum mulai |
| `BOMB_PENALTY` | `20` | Pengurangan skor saat menebas bom |
| `BOMB_CHANCE` | `0.18` | Peluang munculnya bom (0–1) |


## 🔄 Alur Status Game

| Status | Kondisi | Berpindah Ke |
| :--- | :--- | :--- |
| **`countdown`** | Menampilkan "BERSIAP!" dan hitung mundur | `playing` setelah 3 detik |
| **`playing`** | Buah dilempar, tebasan aktif, timer berjalan | `over` ketika waktu habis |
| **`over`** | Menampilkan skor akhir dan rekor | `countdown` saat menekan `R` |


## 🧩 Penjelasan Struktur Kode

### Kelas

- **`Item`**:
  Mewakili buah atau bom yang dilempar dari bawah layar. Menyimpan posisi, kecepatan, warna, dan radius, serta mengarahkan lemparan ke tengah layar.
- **`Half`**:
  Potongan buah setelah ditebas. Dua potongan dibuat dengan arah berlawanan, jatuh karena gravitasi, lalu menghilang setelah beberapa frame.
- **`Splash`**:
  Efek percikan partikel berwarna yang muncul saat buah ditebas.
- **`Game`**:
  Mengelola seluruh status permainan: skor, combo, status (`countdown` / `playing` / `over`), spawn objek, pembaruan fisika, dan penggambaran HUD.

### Fungsi

- **`seg_hits_circle(p1, p2, c, r)`**:
  Mengecek apakah segmen garis dari posisi jari sebelumnya (`p1`) ke posisi sekarang (`p2`) memotong lingkaran objek dengan pusat `c` dan radius `r`.
- **`put_text(...)`**:
  Menggambar teks dengan garis tepi hitam agar tetap terbaca di atas latar kamera.
- **`open_camera()`**:
  Mencari dan membuka kamera yang valid dengan mencoba beberapa index dan backend, lalu memastikan frame bisa dibaca.
- **`main()`**:
  Menjalankan *game loop* utama: membaca frame, mendeteksi jari telunjuk, memeriksa tebasan, memperbarui dan menggambar game, lalu menangani input keyboard.

### Cara Kerja Singkat

1. Frame kamera dibaca, dicerminkan, di-resize, dan diredupkan.
2. MediaPipe mendeteksi tangan dan mengambil posisi ujung jari telunjuk.
3. Kecepatan jari dihitung dari selisih posisi antar frame.
4. Jika kecepatan melebihi `SLICE_SPEED`, segmen tebasan diperiksa terhadap semua objek di layar.
5. Skor, efek, dan HUD diperbarui lalu ditampilkan di jendela OpenCV.


## 🩺 Pemecahan Masalah

| Masalah | Solusi |
| :--- | :--- |
| **"Tidak ada kamera yang bisa dibaca"** | Tutup aplikasi lain yang memakai kamera (Zoom, Teams, browser). Di Windows, cek izin kamera pada **Settings > Privacy > Camera**. |
| **Tangan sulit terdeteksi** | Perbaiki pencahayaan dan pastikan tangan terlihat jelas di depan kamera. |
| **Tebasan tidak terdeteksi** | Gerakkan jari lebih cepat atau turunkan nilai `SLICE_SPEED`. |
| **FPS rendah / game patah-patah** | Turunkan resolusi (`WIDTH`, `HEIGHT`) dan tutup aplikasi lain yang berat. |
| **Error saat instalasi MediaPipe** | Pastikan versi Python didukung (3.8 – 3.12) dan gunakan `mediapipe==0.10.14`. |


# 🎯 Tujuan Proyek

Proyek ini dibuat sebagai latihan dalam mengembangkan game interaktif berbasis visi komputer dengan menerapkan:

- Pelacakan tangan *real-time* menggunakan MediaPipe
- Pengolahan video dan penggambaran grafis dengan OpenCV
- Struktur kode berorientasi objek yang rapi dan mudah dipelihara
- Simulasi fisika sederhana (gravitasi, lemparan, dan potongan buah)
- Deteksi tabrakan antara garis dan lingkaran
- Pengelolaan status game menggunakan *state machine* sederhana


# 🚀 Rencana Pengembangan

Beberapa fitur yang akan dikembangkan di masa mendatang:

- 💾 Penyimpanan skor tertinggi ke file agar tidak hilang setelah game ditutup
- 🔊 Efek suara dan musik latar
- 📈 Tingkat kesulitan bertahap (kecepatan dan jumlah objek meningkat)
- ❤️ Mode nyawa (*lives*) sebagai alternatif mode waktu
- 🍌 Penambahan jenis buah dan *power-up* spesial
- 🖼️ Penggunaan gambar/sprite buah menggantikan lingkaran


## 📜 Lisensi

Proyek ini dibuat untuk tujuan edukasi dan portofolio pengembangan aplikasi Computer Vision. Silakan kembangkan dan kustomisasi sesuai kebutuhan Anda.

<div align="center">

### ⭐ Jangan lupa berikan Star jika proyek ini bermanfaat!

Created by [username-anda](https://github.com/username-anda)

</div>
