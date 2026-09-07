import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df

def inspect_data(df) :
    print("--- 5 baris pertama ---")
    print(df.head())

    print("\n--- Jumlah baris dan kolom ---")
    print(df.shape)

    print("\n--- Nama kolom ---")
    print(df.columns.tolist())

    print("--- Tipe data tiap kolom ---")
    print(df.dtypes)

    print("\n--- Jumlah missing values per kolom ---")
    print(df.isnull().sum())

    print("\n--- Jumlah baris duplikat ---")
    print(df.duplicated().sum())

    print("\n--- Nilai unik kolom kategorikal ---")
    kolom_kategorikal = ["make", "body-style", "drive-wheels", "fuel-system", "num-of-doors"]
    for kolom in kolom_kategorikal :
        print(f"{kolom} : {df[kolom].unique()}")

def clean_data(df):
    # 1. bikin kolom kategorikal jadi huruf kecil semua + hapus spasi nyasar
    kolom_kategorikal = ["make", "body-style", "drive-wheels", "fuel-system", "num-of-doors"]
    for kolom in kolom_kategorikal:
        df[kolom] = df[kolom].str.strip().str.lower()
    print("Selesai membersihkan penulisan kategori (huruf kecil + hapus spasi)")

    # 2. ubah transaction_date jadi format tanggal standar
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="mixed", errors="coerce")
    print("Selesai menstandarkan format transaction_date")

    # 3. isi missing value di kolom angka pakai median (nilai tengah)
    df["stroke"] = df["stroke"].fillna(df["stroke"].median())
    df["horsepower"] = df["horsepower"].fillna(df["horsepower"].median())
    print("Selesai mengisi missing value di stroke & horsepower pakai median")

    # 4. isi horsepower-binned yang kosong berdasarkan nilai horsepower
    def kategori_horsepower(hp):
        if hp < 100:
            return "low"
        elif hp < 175:
            return "medium"
        else:
            return "high"

    mask_kosong = df["horsepower-binned"].isnull()
    df.loc[mask_kosong, "horsepower-binned"] = df.loc[mask_kosong, "horsepower"].apply(kategori_horsepower)
    print("Selesai mengisi horsepower-binned yang kosong berdasarkan nilai horsepower")

    # 5. baris yang kolom price-nya kosong, baris dihapus, karena nebak harga itu berisiko/nggak akurat, dan cuma 3 baris jadi dampaknya kecil
    df = df.dropna(subset=["price"])
    print("Selesai menghapus baris yang price-nya kosong")

    # 6. missing value di kolom kategorikal make, isi dengan 'unknown'
    df["make"] = df["make"].fillna("unknown")
    print("Selesai mengisi make yang kosong dengan 'unknown'")

    # 7. missing value di num-of-doors, isi dengan nilai yang paling sering muncul
    nilai_terbanyak = df["num-of-doors"].mode()[0]
    df["num-of-doors"] = df["num-of-doors"].fillna(nilai_terbanyak)
    print(f"Selesai mengisi num-of-doors yang kosong dengan '{nilai_terbanyak}'")

    # 8. hapus baris yang isinya duplikat semua
    jumlah_sebelum = len(df)
    df = df.drop_duplicates()
    jumlah_sesudah = len(df)
    print(f"Selesai menghapus duplikat: {jumlah_sebelum - jumlah_sesudah} baris dihapus")

    return df

def transform_data(df):
    # normalisasi horsepower jadi skala 0-1
    hp_min = df["horsepower"].min()
    hp_max = df["horsepower"].max()
    df["horsepower-normalized"] = (df["horsepower"] - hp_min) / (hp_max - hp_min)
    print("Selesai normalisasi horsepower -> horsepower-normalized (0-1)")

    # encoding body-style jadi kolom angka 0/1
    dummy_kolom = pd.get_dummies(df["body-style"], prefix="body-style")
    df = pd.concat([df, dummy_kolom], axis=1)
    print(f"Selesai encoding body-style -> kolom baru: {dummy_kolom.columns.tolist()}")

    return df

def save_data(df, path):
    df.to_csv(path, index=False)
    print(f"Dataset berhasil disimpan di: {path}")

def run_pipeline():
    df = load_data("data/raw/automobileEDA_dirty_training.csv")
    inspect_data(df)
    df = clean_data(df)
    inspect_data(df)
    df = transform_data(df)
    print(df[["horsepower", "horsepower-normalized"]].head())
    print(df.filter(like="body-style").head())
    save_data(df, "data/processed/automobileEDA_processed.csv")

if __name__ == "__main__":
    run_pipeline()