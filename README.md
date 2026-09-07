# Automobile Data Pipeline — Individual Assignment

Pipeline sederhana untuk mengolah dataset otomotif dari data mentah menjadi
dataset siap pakai untuk analisis/pemodelan, mengikuti konsep **ETL
(Extract → Transform → Load)**.

## 1. Deskripsi Dataset

Dataset berisi data spesifikasi teknis dan harga mobil (automobile), meliputi
atribut seperti merek (`make`), tipe bodi, jumlah pintu, dimensi, tenaga
mesin (`horsepower`), konsumsi bahan bakar, dan harga (`price`). Dataset yang
digunakan sebagai input pipeline adalah versi "dirty" yang sengaja mengandung
missing values, duplikat, dan inkonsistensi penulisan kategori.

## 2. Sumber Dataset

Dataset diperoleh dari link yang diberikan pada assignment:
`https://s.id/dataset-sesi-3` (file `Dataset_Sesi_3.zip`).

File yang digunakan:
- `automobileEDA_dirty_training.csv` — dataset utama (input pipeline)
- `automobileEDA.csv` — dataset original (referensi)
- `automobile_processed.csv` — dataset bersih (referensi/pembanding hasil, tidak dipakai sebagai output)

## 3. Struktur Folder Project

data-pipeline-assignment/
- data/
  - raw/
    - automobileEDA_dirty_training.csv
  - processed/
    - automobileEDA_processed.csv
- src/
  - pipeline.py
- documentation/
  - data-flow-diagram.png
- README.md
- requirements.txt

## 4. Kondisi Awal Dataset

- Ukuran awal: **205 baris x 30 kolom**
- Kolom dengan missing values:

  | Kolom | Jumlah kosong |
  |---|---|
  | transaction_date | 2 |
  | make | 2 |
  | num-of-doors | 2 |
  | stroke | 4 |
  | horsepower | 3 |
  | price | 3 |
  | horsepower-binned | 1 |

  Total: **17 missing values**

- Baris terduplikasi: **4 baris**
- Tipe data belum sesuai: `transaction_date` terbaca sebagai teks (string),
  seharusnya bertipe `datetime`.

## 5. Permasalahan yang Ditemukan

1. **Missing values** pada 7 kolom (lihat tabel di atas).
2. **Duplicate records** — 4 baris identik.
3. **Penulisan kategori tidak konsisten**, contoh:
   - `make`: 28 nilai unik, padahal seharusnya lebih sedikit — campur
     `alfa-romero` vs `ALFA-ROMERO`, `audi` vs `Audi`, `bmw` vs
     `BMW`, plus spasi berlebih seperti `dodge  `, `mercury  `, `porsche  `
   - `body-style`: 7 nilai unik — `sedan` vs `SEDAN` vs `Sedan`
   - `drive-wheels`: 5 nilai unik — `rwd` vs `RWD`, `awd` vs `AWD`
   - `fuel-system`: 10 nilai unik — `mpfi` vs `MPFI` vs `Mpfi`
4. **Format tanggal tidak konsisten** pada `transaction_date` — bercampur
   beberapa format (2025-01-01, 02/01/2025, 01-03-2025, 04-Jan-2025, dll).
5. **Tipe data belum sesuai** — `transaction_date` masih berupa string.

## 6. Cleaning yang Dilakukan Beserta Alasannya

| Kolom | Masalah | Metode Cleaning | Alasan |
|---|---|---|---|
| make, body-style, drive-wheels, fuel-system, num-of-doors | Penulisan tidak konsisten (huruf besar/kecil, spasi) | strip() + lowercase | Menyamakan representasi kategori yang sebenarnya sama tanpa mengubah makna data |
| transaction_date | Format tanggal campur-campur | Parse ke datetime dengan pd.to_datetime(format="mixed") | Menstandarkan tipe data agar konsisten dan bisa diproses/diurutkan |
| stroke, horsepower | Missing values (numerik) | Diisi dengan median | Median tahan terhadap outlier dan mempertahankan jumlah baris |
| horsepower-binned | Missing value (kategorikal, turunan dari horsepower) | Dihitung ulang dari nilai horsepower yang sudah bersih | Lebih akurat daripada menebak, karena bisa diturunkan langsung dari kolom sumbernya |
| price | Missing values | Baris dihapus | price adalah kolom penting untuk analisis; baris tanpa harga tidak informatif dan hanya 3 baris (dampak minim) |
| make | Missing values (kategorikal) | Diisi dengan 'unknown' | Mempertahankan baris karena kolom lain tetap punya nilai berguna |
| num-of-doors | Missing values (kategorikal) | Diisi dengan modus ('four') | Nilai paling umum adalah tebakan paling wajar untuk kategori biner ini |
| Seluruh dataset | 4 baris duplikat | drop_duplicates() | Baris identik tidak menambah informasi dan berpotensi bias hasil analisis |

**Hasil cleaning:**
- Jumlah baris: 205 → **198** (setelah drop duplikat + baris price kosong)
- Total missing values: 17 → **2** (sisa 2 baris transaction_date yang
  formatnya benar-benar tidak bisa dikenali/rusak; dibiarkan kosong karena
  menebak tanggal tidak masuk akal)
- Duplicate rows dihapus: **4**
- Nilai unik kategori setelah dibersihkan:

  | Kolom | Sebelum | Sesudah |
  |---|---|---|
  | make | 28 | 23 |
  | body-style | 7 | 5 |
  | drive-wheels | 5 | 4 |
  | fuel-system | 10 | 8 |
  | num-of-doors | 3 | 2 |

## 7. Transformasi yang Dilakukan

| Kolom | Metode | Alasan Pemilihan |
|---|---|---|
| horsepower | Min-Max Scaling → kolom baru horsepower-normalized (0–1) | horsepower punya rentang nilai lebar dan relevan sebagai fitur numerik untuk pemodelan; Min-Max Scaling menyamakan skalanya dengan fitur numerik lain |
| body-style | One-Hot Encoding → kolom baru body-style_convertible, body-style_hardtop, body-style_hatchback, body-style_sedan, body-style_wagon | Kolom kategorikal dengan kardinalitas rendah (5 kategori setelah cleaning), cocok untuk one-hot encoding tanpa membuat dimensi data membengkak |

### Contoh Nilai Sebelum vs Sesudah Transformasi

**Min-Max Scaling (horsepower):**

| horsepower (sebelum) | horsepower-normalized (sesudah) |
|---|---|
| 111.0 | 0.294393 |
| 111.0 | 0.294393 |
| 154.0 | 0.495327 |
| 102.0 | 0.252336 |
| 115.0 | 0.313084 |

**One-Hot Encoding (body-style):**

| body-style (sebelum) | body-style_convertible | body-style_hatchback | body-style_sedan | body-style_wagon | body-style_hardtop |
|---|---|---|---|---|---|
| convertible | True | False | False | False | False |
| hatchback | False | True | False | False | False |
| sedan | False | False | True | False | False |

## 8. Jumlah Data Sebelum dan Sesudah Diproses

| | Baris | Kolom |
|---|---|---|
| Sebelum (raw) | 205 | 30 |
| Sesudah (processed) | 198 | 36 |

(Penambahan kolom berasal dari horsepower-normalized + 5 kolom hasil
one-hot encoding body-style.)

## 9. Cara Instalasi Dependency

Buat dan aktifkan virtual environment, lalu install dependency:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## 10. Cara Menjalankan Pipeline

    python src/pipeline.py

Menjalankan perintah di atas akan otomatis:
1. Membaca dataset mentah dari data/raw/
2. Menampilkan laporan inspeksi awal di terminal
3. Melakukan cleaning dan menampilkan ringkasan sebelum/sesudah
4. Melakukan transformasi (normalisasi + encoding)
5. Menyimpan dataset hasil ke data/processed/automobileEDA_processed.csv

## 11. Alur ETL

| Tahap | Proses | Function |
|---|---|---|
| Extract | Membaca dataset CSV dari data/raw/ | load_data() |
| Transform | Memeriksa kondisi data, membersihkan, dan mentransformasi | inspect_data(), clean_data(), transform_data() |
| Load | Menyimpan processed dataset ke data/processed/ | save_data() |

Seluruh tahapan digabung dan dijalankan berurutan dalam satu eksekusi melalui
run_pipeline().

## 12. Lokasi Processed Dataset

    data/processed/automobileEDA_processed.csv

Dataset ini dihasilkan otomatis setiap kali pipeline.py dijalankan, bukan
disalin dari automobile_processed.csv yang menjadi referensi mentor.
Dataset mentah di data/raw/ tidak diubah sama sekali oleh pipeline.
