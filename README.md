# WaitList-Fair

> **WaitList-Fair** adalah prototipe sistem prioritisasi jadwal radioterapi berbasis skor risiko klinis dan faktor fairness sosial untuk membantu proses triase pasien onkologi secara lebih terstruktur, transparan, dan dapat diaudit.

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-20232a?logo=react)
![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)

---

## 📌 Ringkasan Proyek

Pada praktik klinis, antrean radioterapi sering diprioritaskan berdasarkan kebijakan lokal dan judgement manual. Pendekatan ini cepat, tetapi berpotensi inkonsisten ketika volume pasien tinggi. **WaitList-Fair** menawarkan simulasi scoring yang:

- Mengestimasi **risiko progresi saat menunggu** (_progression-while-waiting_).
- Menambahkan komponen **fairness boost** berbasis kerentanan sosial ekonomi.
- Menghasilkan **urutan prioritas** yang mudah dibaca tim klinis.
- Menyediakan metrik sederhana untuk memantau **kesenjangan antarkelompok**.

> ⚠️ **Catatan penting:** proyek ini adalah prototipe edukasional/research awal, **bukan** sistem keputusan klinis final.

---

## 🧠 Analisis Codebase (Detail & Mendalam)

## 1) Arsitektur Umum

Repository dibagi menjadi dua lapisan:

- **Backend (`backend/`)**: API FastAPI untuk validasi data pasien, perhitungan skor, sorting prioritas, dan kalkulasi metrik fairness.
- **Frontend (`frontend/`)**: UI React sederhana untuk input JSON pasien dan visualisasi hasil prioritas.

Alur data:

1. Pengguna mengisi/mengubah JSON pasien di frontend.
2. Frontend mengirim payload ke endpoint `POST /prioritize`.
3. Backend menghitung `risk_score`, `fairness_boost`, dan `priority_score` per pasien.
4. Backend mengurutkan hasil (descending `priority_score`) dan mengembalikan metrik agregat.
5. Frontend menampilkan tabel prioritas + ringkasan metrik.

---

## 2) Analisis Backend (FastAPI)

File utama: `backend/main.py`.

### A. Kontrak Data (Pydantic Models)

Backend menggunakan model input ketat untuk menjaga kualitas data:

- `patient_id` (string)
- `age` (0–120)
- `waiting_days` (>=0)
- `stage` (1–4)
- `ecog` (0–4)
- `tumor_growth_rate` (0.0–1.0)
- `socioeconomic_index` (0.0–1.0)
- `group` (string kategori fairness)

**Dampak desain:**
- Mencegah input absurd sejak awal (mis. stadium >4).
- Memudahkan tracing bila integrasi ke HIS/EMR dilakukan.
- Kontrak API sudah self-documented via FastAPI docs.

### B. Formula Risiko dan Bobot

Skor risiko dibangun dari bobot tetap (`RiskWeights`) dengan total bobot = 1.0:

- waiting_days: **0.22**
- stage: **0.28**
- ecog: **0.15**
- tumor_growth_rate: **0.25**
- age: **0.05**
- socioeconomic_index: **0.05**

Fungsi normalisasi:

- `normalize_waiting_days(days)` → skala 0..1, saturasi di 90 hari.
- `normalize_age(age)` → mulai berdampak setelah 40 tahun.

Perhitungan inti:

- `risk_score = Σ(weight_i * feature_i_normalized)`
- nilai dikunci pada rentang 0..1 dan dibulatkan 4 desimal.

**Kekuatan desain:**
- Mudah dijelaskan ke stakeholder non-teknis.
- Deterministik dan bisa direplikasi untuk audit.

**Batasan desain:**
- Belum ada pembelajaran data-driven (masih rule-based weighted score).
- Belum ada kalibrasi terhadap outcome real-world.

### C. Komponen Fairness

`fairness_boost = 0.08 * socioeconomic_index`

Lalu:

- `priority_score = min(risk_score + fairness_boost, 1.0)`

**Makna praktis:**
- Pasien dengan kerentanan sosial lebih tinggi mendapat dorongan skor kecil agar tidak tertinggal karena hambatan non-klinis.

**Keterbatasan:**
- Fairness masih satu dimensi (hanya socioeconomic index).
- Belum ada fairness constraints formal (mis. demographic parity/equalized odds).

### D. Output dan Metrik

Response API mengembalikan:

- `manual_baseline`: baseline naratif prioritisasi manual.
- `prioritized`: daftar pasien berisi:
  - `risk_score`
  - `fairness_boost`
  - `priority_score`
  - `estimated_wait_impact` (= risk_score × waiting_days)
  - `suggested_priority` (`LOW` / `MEDIUM` / `HIGH`)
- `metrics`:
  - `high_risk_count`
  - `avg_priority_by_group`
  - `equity_gap` (selisih rata-rata skor tertinggi vs terendah antarkelompok)

**Insight:**
- `equity_gap` berperan sebagai indikator cepat apakah satu kelompok tampak tertinggal/terdorong berlebihan.

---

## 3) Analisis Frontend (React + Vite)

File utama: `frontend/src/App.jsx` dan `frontend/src/styles.css`.

### A. Pola Interaksi

- Frontend menyediakan `textarea` JSON untuk fleksibilitas input batch.
- Ada sample patients default untuk demo cepat.
- Tombol `Hitung Prioritas` memicu request async ke backend.
- Error handling menampilkan pesan bila parsing JSON / API gagal.

### B. Presentasi Hasil

UI menampilkan:

- Baseline manual.
- Jumlah pasien high-risk.
- Rata-rata dampak tunggu untuk high-risk (`useMemo`).
- Equity gap.
- Rata-rata skor per kelompok.
- Tabel urutan prioritas.

**Kelebihan:**
- Sangat cepat dipahami oleh user teknis/non-teknis.
- Cukup untuk proof-of-concept diskusi klinis.

**Area upgrade:**
- Form terstruktur per field (bukan JSON bebas) untuk mengurangi human error.
- Validasi frontend yang konsisten dengan backend.
- Filtering/sorting tabel langsung di UI.

---

## 4) Kekuatan, Risiko, dan Rekomendasi Pengembangan

### Kekuatan Saat Ini

- Implementasi ringan dan mudah dijalankan lokal.
- Transparan (rule-based) sehingga mudah diaudit.
- Sudah memuat fairness dalam bentuk awal.
- API dan UI siap sebagai fondasi iterasi riset.

### Risiko / Gap

- Belum tervalidasi klinis pada data nyata.
- Bobot belum dipelajari dari cohort historis.
- Belum ada autentikasi, logging audit klinis, dan role-based access.
- Belum ada persistence database (hasil masih stateless in-memory per request).

### Rekomendasi Lanjutan (Roadmap)

1. Integrasi database + audit trail.
2. Validasi model pada data retrospektif multi-center.
3. Eksperimen bobot adaptif berbasis outcome.
4. Tambahkan fairness metrics yang lebih formal.
5. Dashboard operasional (tren waiting time, drift, subgroup monitoring).
6. Hardening security (authN/authZ, request signing, API gateway).

---

## ✨ Fitur Utama

- **Risk scoring klinis** berbasis multi-faktor.
- **Fairness-aware prioritization** melalui social vulnerability boost.
- **Ranking otomatis** pasien dari skor tertinggi ke terendah.
- **Label prioritas klinis**: `LOW`, `MEDIUM`, `HIGH`.
- **Metrik ringkasan fairness** per kelompok.
- **Frontend interaktif** untuk simulasi cepat.
- **Dokumentasi API otomatis** via Swagger UI.

---

## ⚙️ Fungsi Inti Sistem

- Menerima batch data pasien.
- Menstandarkan fitur numerik melalui normalisasi.
- Menghitung skor risiko progression-while-waiting.
- Menambahkan komponen fairness ke skor akhir.
- Mengurutkan kandidat prioritas terapi.
- Menyajikan metrik agregat untuk monitoring.

---

## 🗂️ Struktur Folder

```bash
.
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
└── README.md
```

---

## 🚀 Cara Menjalankan

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- Swagger docs: `http://localhost:8000/docs`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

- Frontend URL: `http://localhost:5173`

---

## 🔌 API Reference

### `GET /health`
Respons cepat untuk cek status service.

### `POST /prioritize`
Hitung prioritas pasien.

**Contoh request:**

```json
{
  "patients": [
    {
      "patient_id": "P-001",
      "age": 57,
      "waiting_days": 35,
      "stage": 3,
      "ecog": 1,
      "tumor_growth_rate": 0.6,
      "socioeconomic_index": 0.7,
      "group": "BPJS-Regional"
    }
  ]
}
```

---

## 🧪 Teknologi

- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** React, Vite
- **Bahasa:** Python, JavaScript

---

## 👤 Author

**Lettu Kes dr. Muhammad Sobri Maulana, S.Kom, CEH, OSCP, OSCE**

- GitHub: [github.com/sobri3195](https://github.com/sobri3195)
- Email: [muhammadsobrimaulana31@gmail.com](mailto:muhammadsobrimaulana31@gmail.com)
- Website: [muhammadsobrimaulana.netlify.app](https://muhammadsobrimaulana.netlify.app)
- YouTube: [@muhammadsobrimaulana6013](https://www.youtube.com/@muhammadsobrimaulana6013)
- Telegram: [winlin_exploit](https://t.me/winlin_exploit)
- TikTok: [@dr.sobri](https://www.tiktok.com/@dr.sobri)
- Grup WhatsApp: [Join Group](https://chat.whatsapp.com/B8nwRZOBMo64GjTwdXV8Bl)
- Sevalla Page: [muhammad-sobri-maulana-kvr6a.sevalla.page](https://muhammad-sobri-maulana-kvr6a.sevalla.page/)
- Toko Online Sobri: [pegasus-shop.netlify.app](https://pegasus-shop.netlify.app)

---

## ❤️ Donasi & Dukungan

Terima kasih atas dukungan untuk pengembangan riset dan edukasi keamanan/kesehatan digital.

- Lynk: [lynk.id/muhsobrimaulana](https://lynk.id/muhsobrimaulana)
- Trakteer: [trakteer.id/g9mkave5gauns962u07t](https://trakteer.id/g9mkave5gauns962u07t)
- Gumroad: [maulanasobri.gumroad.com](https://maulanasobri.gumroad.com/)
- KaryaKarsa: [karyakarsa.com/muhammadsobrimaulana](https://karyakarsa.com/muhammadsobrimaulana)
- Nyawer: [nyawer.co/MuhammadSobriMaulana](https://nyawer.co/MuhammadSobriMaulana)

---

## 📄 Lisensi

Belum ditentukan. Disarankan menambahkan lisensi resmi (MIT/Apache-2.0/GPL) agar penggunaan dan kontribusi lebih jelas.
