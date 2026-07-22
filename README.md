# Gemini Remover Watermark
```markdown
# 🎬 Video Utility & Watermark Cleaner

Aplikasi web berbasis Python menggunakan framework **Streamlit** dan **OpenCV** untuk membersihkan atau menyamarkan area tertentu pada video (seperti watermark atau logo di sudut video) secara otomatis menggunakan teknik *inpainting*.

## ✨ Fitur Utama
* **Unggah Video Fleksibel:** Mendukung berbagai format video umum seperti MP4, MOV, dan AVI.
* **Pengaturan Area Kustom:** Sidebar interaktif untuk memilih posisi area (sudut kanan/kiri atas/bawah), mengatur lebar, tinggi, serta jarak dari tepian video.
* **Proses Otomatis:** Menggunakan algoritma *inpainting* OpenCV untuk mengisi area watermark dengan latar belakang di sekitarnya secara mulus.
* **Pratinjau & Unduh:** Menampilkan video asli serta hasil video yang sudah bersih dengan tombol unduh langsung.

## 🛠️ Teknologi yang Digunakan
* [Python](https://www.python.org/)
* [Streamlit](https://streamlit.io/)
* [OpenCV (opencv-python-headless)](https://opencv.org/)
* [NumPy](https://numpy.org/)

## 🚀 Cara Menjalankan Secara Lokal

1. Clone repository ini:
   ```bash
   git clone [https://github.com/KurniaErawati/geminiremovewatermark.git](https://github.com/KurniaErawati/geminiremovewatermark.git)
   cd geminiremovewatermark

```

2. Instal dependensi yang dibutuhkan:
```bash
pip install -r requirements.txt

```


3. Jalankan aplikasi Streamlit:
```bash
streamlit run app.py
