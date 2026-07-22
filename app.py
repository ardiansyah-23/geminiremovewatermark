import tempfile
import cv2
import numpy as np
import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Auto-Detect Video Watermark Cleaner",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 Utilitas Pembersih Watermark Otomatis")
st.write(
    "Unggah video dan gambar acuan (template) watermark yang ingin dihapus secara otomatis!"
)

# Sidebar untuk Pengaturan Mode
st.sidebar.header("⚙️ Pengaturan Mode")
mode = st.sidebar.radio(
    "Pilih Metode Deteksi:",
    ["Manual (Geser Kotak)", "Otomatis (Template Matching)"],
)

uploaded_file = st.file_uploader(
    "Pilih file video (MP4, MOV, AVI):", type=["mp4", "mov", "avi"]
)

# Jika mode otomatis, minta pengguna mengunggah gambar watermark kecil yang dicari
template_file = None
if mode == "Otomatis (Template Matching)":
  template_file = st.file_uploader(
      "Unggah gambar contoh watermark (logo kecil / PNG/JPG):",
      type=["png", "jpg", "jpeg"],
  )
else:
  # Pengaturan manual seperti sebelumnya
  box_width = st.sidebar.slider("Lebar Kotak (px)", 50, 300, 150)
  box_height = st.sidebar.slider("Tinggi Kotak (px)", 20, 150, 50)
  margin = st.sidebar.slider("Jarak dari Tepian (px)", 5, 50, 15)
  position = st.sidebar.selectbox(
      "Pilih Posisi Area:",
      [
          "Kanan Bawah (Bottom-Right)",
          "Kiri Bawah (Bottom-Left)",
          "Kanan Atas (Top-Right)",
          "Kiri Atas (Top-Left)",
      ],
  )

if uploaded_file is not None:
  tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
  tfile.write(uploaded_file.read())
  video_path = tfile.name

  st.subheader("🎥 Video Asli")
  st.video(video_path)

  # Validasi jika mode otomatis tapi belum upload template
  can_process = True
  if mode == "Otomatis (Template Matching)" and template_file is None:
    st.warning("⚠️ Silakan unggah gambar contoh watermark terlebih dahulu!")
    can_process = False

  if can_process and st.button("🚀 Proses Video Sekarang", type="primary"):
    with st.spinner("Sedang memproses dan mendeteksi watermark..."):
      cap = cv2.VideoCapture(video_path)
      fps = int(cap.get(cv2.CAP_PROP_FPS))
      width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
      height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
      total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

      # Baca template gambar jika mode otomatis
      template = None
      t_w, t_h = 0, 0
      if mode == "Otomatis (Template Matching)" and template_file is not None:
        file_bytes = np.asarray(
            bytearray(template_file.read()), dtype=np.uint8
        )
        template = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        t_h, t_w = template.shape[:2]

      output_tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
      output_path = output_tfile.name

      fourcc = cv2.VideoWriter_fourcc(*"mp4v")
      out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

      progress_bar = st.progress(0)
      frame_count = 0

      while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
          break

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        if mode == "Otomatis (Template Matching)" and template is not None:
          # Konversi frame ke grayscale untuk pencocokan
          gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

          # Lakukan template matching
          result = cv2.matchTemplate(
              gray_frame, template, cv2.METHOD_CCOEFF_NORMED
          )
          threshold = 0.7  # Tingkat kecocokan (70%)
          loc = np.where(result >= threshold)

          # Tandai semua area yang cocok di dalam mask
          for pt in zip(*loc[::-1]):
            mask[pt[1] : pt[1] + t_h, pt[0] : pt[0] + t_w] = 255
        else:
          # Logika Manual
          if position == "Kanan Bawah (Bottom-Right)":
            x1 = width - box_width - margin
            y1 = height - box_height - margin
          elif position == "Kiri Bawah (Bottom-Left)":
            x1 = margin
            y1 = height - box_height - margin
          elif position == "Kanan Atas (Top-Right)":
            x1 = width - box_width - margin
            y1 = margin
          else:
            x1 = margin
            y1 = margin

          x2 = x1 + box_width
          y2 = y1 + box_height
          mask[y1:y2, x1:x2] = 255

        # Terapkan inpainting berdasarkan mask yang terbentuk
        processed_frame = cv2.inpaint(
            frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA
        )
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

    with open(output_path, "rb") as file:
      st.download_button(
          label="📥 Download Video Hasil",
          data=file,
          file_name="video_cleaned.mp4",
          mime="video/mp4",
      )
