# WaitList-Fair

**WaitList-Fair** adalah prototipe aplikasi _React + Python_ untuk membantu prioritisasi jadwal radioterapi pada pasien onkologi yang sedang menunggu slot terapi.

**Author:** dr. Muhammad Sobri Maulana  

## Latar belakang (PICO)

### 9) WaitList-Fair: Prioritisasi Jadwal Radioterapi Berbasis AI untuk Meminimalkan Risiko Progresi Saat Menunggu

- **P (Population):** Pasien onkologi yang menunggu slot radioterapi.
- **I (Intervention):** Model AI yang mengestimasi risiko _progression-while-waiting_ untuk prioritas penjadwalan.
- **C (Comparison):** Prioritisasi manual berdasarkan kebijakan dan judgement klinis.
- **O (Outcomes):**
  - Waktu tunggu pada kelompok high-risk
  - Outcome klinis (misalnya _stage migration_ / _response_)
  - Metrik fairness (equity antar kelompok)

## Arsitektur

- **Backend (Python / FastAPI):**
  - Endpoint `/prioritize` menerima daftar pasien
  - Menghitung `risk_score` progression-while-waiting
  - Menambahkan `fairness_boost` untuk kelompok lebih rentan
  - Menghasilkan urutan prioritas dan metrik fairness (`equity_gap`)
- **Frontend (React + Vite):**
  - Input data pasien dalam format JSON
  - Menampilkan hasil prioritas, ringkasan high-risk, dan metrik fairness

## Struktur Folder

```bash
.
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
└── README.md
```

## Cara Menjalankan

### 1) Jalankan Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend tersedia di: `http://localhost:8000`  
Dokumentasi API: `http://localhost:8000/docs`

### 2) Jalankan Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Frontend tersedia di: `http://localhost:5173`

## Contoh Payload API

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

## Catatan Klinis

Model ini adalah **prototipe edukasional** untuk simulasi keputusan penjadwalan. Implementasi klinis nyata memerlukan:

1. Validasi data retrospektif/prospektif
2. Tata kelola AI rumah sakit
3. Persetujuan etik dan regulasi
4. Integrasi multidisciplinary tumor board
