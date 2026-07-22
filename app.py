import tempfile
import cv2
import numpy as np
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Video Utility & Watermark Cleaner",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 Utilitas Pembersih Area Video")
st.write(
    "Unggah video kamu, tentukan area yang ingin dibersihkan (misalnya sudut video), lalu proses hasilnya!"
)

# Sidebar untuk Pengaturan
st.sidebar.header("⚙️ Pengaturan Area")
st.sidebar.write("Sesuaikan koordinat area yang ingin diproses/dibersihkan.")

# Pilihan posisi sudut umum
position = st.sidebar.selectbox(
    "Pilih Posisi Area:",
    [
        "Kanan Bawah (Bottom-Right)",
        "Kiri Bawah (Bottom-Left)",
        "Kanan Atas (Top-Right)",
        "Kiri Atas (Top-Left)",
    ],
)

# Ukuran kotak area yang akan dibersihkan
box_width = st.sidebar.slider("Lebar Kotak (px)", 50, 300, 150)
box_height = st.sidebar.slider("Tinggi Kotak (px)", 20, 150, 50)
margin = st.sidebar.slider("Jarak dari Tepian (px)", 5, 50, 15)

# Komponen Unggah File Video (Mendukung file hingga batas config.toml)
uploaded_file = st.file_uploader(
    "Pilih file video (MP4, MOV, AVI):", type=["mp4", "mov", "avi"]
)

if uploaded_file is not None:
  # Simpan video yang diunggah ke file sementara
  tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
  tfile.write(uploaded_file.read())
  video_path = tfile.name

  st.subheader("🎥 Video Asli")
  st.video(video_path)

  if st.button("🚀 Proses Video Sekarang", type="primary"):
    with st.spinner(
        "Sedang memproses bingkai video... Mohon tunggu sebentar."
    ):
      # Buka video menggunakan OpenCV
      cap = cv2.VideoCapture(video_path)
      fps = int(cap.get(cv2.CAP_PROP_FPS))
      width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
      height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
      total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

      # Buat file output sementara untuk hasil video
      output_tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
      output_path = output_tfile.name

      # Inisialisasi Video Writer (menggunakan codec mp4v)
      fourcc = cv2.VideoWriter_fourcc(*"mp4v")
      out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

      progress_bar = st.progress(0)
      frame_count = 0

      while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
          break

        # Tentukan koordinat berdasarkan pilihan posisi
        if position == "Kanan Bawah (Bottom-Right)":
          x1 = width - box_width - margin
          y1 = height - box_height - margin
        elif position == "Kiri Bawah (Bottom-Left)":
          x1 = margin
          y1 = height - box_height - margin
        elif position == "Kanan Atas (Top-Right)":
          x1 = width - box_width - margin
          y1 = margin
        else:  # Kiri Atas (Top-Left)
          x1 = margin
          y1 = margin

        x2 = x1 + box_width
        y2 = y1 + box_height

        # Buat mask untuk teknik inpainting pada area tersebut
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255

        # Terapkan algoritma inpainting OpenCV untuk membersihkan area
        processed_frame = cv2.inpaint(
            frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA
        )

        # Tulis frame yang sudah diproses ke video output
        out.write(processed_frame)

        frame_count += 1
        if total_frames > 0:
          progress_bar.progress(min(frame_count / total_frames, 1.0))

      cap.release()
      out.release()
      progress_bar.empty()

    st.success("✅ Pemrosesan video selesai!")
    st.subheader("✨ Hasil Video Terproses")
    st.video(output_path)

    # Tombol Unduh
    with open(output_path, "rb") as file:
      st.download_button(
          label="📥 Download Video Hasil",
          data=file,
          file_name="video_cleaned.mp4",
          mime="video/mp4",
      )
