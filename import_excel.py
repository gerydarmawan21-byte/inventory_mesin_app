import pandas as pd
from database import session, Mesin
from datetime import datetime

# Ganti dengan path file Excel kamu
file_excel = "data_mesin.xlsx"

# Baca Excel
df = pd.read_excel(file_excel)

for index, row in df.iterrows():
    m = Mesin(
        kode_mesin=row['kode_mesin'],
        nama_mesin=row['nama_mesin'],
        brand=row['brand'],
        sg=row['sg'],
        nomor_dokumen=row['nomor_dokumen'],
        jumlah_mesin=int(row['jumlah_mesin']),
        harga_mesin=float(row['harga_mesin']),
        tanggal_pemasukan=datetime.strptime(str(row['tanggal_pemasukan']), '%Y-%m-%d') if not pd.isna(row['tanggal_pemasukan']) else None,
        tanggal_penjualan=datetime.strptime(str(row['tanggal_penjualan']), '%Y-%m-%d') if not pd.isna(row['tanggal_penjualan']) else None,
        tanggal_sewa=datetime.strptime(str(row['tanggal_sewa']), '%Y-%m-%d') if not pd.isna(row['tanggal_sewa']) else None,
        jumlah_sewa=int(row['jumlah_sewa']) if not pd.isna(row['jumlah_sewa']) else 0,
        tanggal_dikembalikan=datetime.strptime(str(row['tanggal_dikembalikan']), '%Y-%m-%d') if not pd.isna(row['tanggal_dikembalikan']) else None,
        jumlah_mesin_kembali=int(row['jumlah_mesin_kembali']) if not pd.isna(row['jumlah_mesin_kembali']) else 0,
        kondisi_mesin=row['kondisi_mesin'],
        keterangan=row['keterangan']
    )
    session.add(m)

session.commit()
print("Import Excel selesai!")
