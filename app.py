import streamlit as st
import pandas as pd
from database import session, User, Mesin, History
from datetime import datetime, date, time
import io

st.set_page_config(page_title="Inventory Aset Mesin", layout="wide")
st.title("📊 Inventory Aset Mesin")

# ---------------------------
# Sidebar Login
# ---------------------------
if "login" not in st.session_state:
    st.session_state["login"] = False
    st.session_state["role"] = ""

st.sidebar.title("Login")
if not st.session_state["login"]:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login = st.sidebar.button("Login")

    if login:
        user = session.query(User).filter_by(username=username, password=password).first()
        if user:
            st.session_state["login"] = True
            st.session_state["role"] = user.role
            st.sidebar.success(f"Selamat datang, {username}! ({user.role})")
        else:
            st.sidebar.error("Username atau password salah!")
else:
    st.sidebar.success(f"Login sebagai {st.session_state['role']}")
    if st.sidebar.button("Logout"):
        st.session_state["login"] = False
        st.session_state["role"] = ""

# ---------------------------
# Fungsi Parse Tanggal Aman
# ---------------------------
def parse_tanggal(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d")
        except:
            try:
                return pd.to_datetime(val)
            except:
                return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    if isinstance(val, time):
        return datetime.combine(datetime.today(), val)
    return None

# ---------------------------
# Menu utama
# ---------------------------
if st.session_state.get("login", False):
    menu = st.sidebar.radio("Menu", [
        "Lihat Data", "Tambah Mesin", "Edit/Hapus Mesin", "Upload Excel", "Riwayat", "Transaksi"
    ])

    # ---------------------------
    # LIHAT DATA
    # ---------------------------
    if menu == "Lihat Data":
        st.subheader("📋 Daftar Aset Mesin")
        data = session.query(Mesin).all()
        df = pd.DataFrame([(m.id, m.kode_mesin, m.nama_mesin, m.brand, m.sg, m.nomor_dokumen,
                            m.jumlah_mesin, m.harga_mesin, m.tanggal_pemasukan, m.tanggal_penjualan,
                            m.tanggal_sewa, m.jumlah_sewa, m.tanggal_dikembalikan, m.jumlah_mesin_kembali,
                            m.kondisi_mesin, m.keterangan) for m in data],
                          columns=["ID", "Kode Mesin", "Nama Mesin", "Brand", "SG", "Nomor Dokumen",
                                   "Jumlah Mesin", "Harga Mesin", "Tanggal Pemasukan", "Tanggal Penjualan",
                                   "Tanggal Sewa", "Jumlah Sewa", "Tanggal Dikembalikan", "Jumlah Kembali",
                                   "Kondisi", "Keterangan"])
        st.dataframe(df)

        if not df.empty:
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, sheet_name="InventoryMesin")
            buffer.seek(0)
            st.download_button("📥 Export ke Excel", data=buffer,
                               file_name="inventory_mesin.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ---------------------------
    # TAMBAH MESIN
    # ---------------------------
    elif menu == "Tambah Mesin":
        if st.session_state["role"] != "admin":
            st.warning("Hanya admin yang bisa menambah mesin!")
        else:
            st.subheader("➕ Tambah Mesin Baru")
            kode = st.text_input("Kode Mesin")
            nama = st.text_input("Nama Mesin")
            brand = st.text_input("Brand")
            sg = st.text_input("SG")
            nomor_dokumen = st.text_input("Nomor Dokumen")
            jumlah_mesin = st.number_input("Jumlah Mesin", min_value=0, value=0)
            harga_mesin = st.number_input("Harga Mesin", min_value=0.0, value=0.0)
            tanggal_pemasukan = st.date_input("Tanggal Pemasukan", datetime.now())
            tanggal_penjualan = st.date_input("Tanggal Penjualan", None)
            tanggal_sewa = st.date_input("Tanggal Sewa", None)
            jumlah_sewa = st.number_input("Jumlah Sewa", min_value=0, value=0)
            tanggal_dikembalikan = st.date_input("Tanggal Dikembalikan", None)
            jumlah_mesin_kembali = st.number_input("Jumlah Mesin Kembali", min_value=0, value=0)
            kondisi = st.selectbox("Kondisi Mesin", ["Baik", "Rusak", "Maintenance"])
            keterangan = st.text_area("Keterangan")

            if st.button("Simpan"):
                try:
                    exist = session.query(Mesin).filter_by(kode_mesin=kode).first()
                    if exist:
                        st.warning("Kode mesin sudah ada!")
                    else:
                        m = Mesin(
                            kode_mesin=kode,
                            nama_mesin=nama,
                            brand=brand,
                            sg=sg,
                            nomor_dokumen=nomor_dokumen,
                            jumlah_mesin=jumlah_mesin,
                            harga_mesin=harga_mesin,
                            tanggal_pemasukan=datetime.combine(tanggal_pemasukan, datetime.min.time()),
                            tanggal_penjualan=datetime.combine(tanggal_penjualan, datetime.min.time()) if tanggal_penjualan else None,
                            tanggal_sewa=datetime.combine(tanggal_sewa, datetime.min.time()) if tanggal_sewa else None,
                            jumlah_sewa=jumlah_sewa,
                            tanggal_dikembalikan=datetime.combine(tanggal_dikembalikan, datetime.min.time()) if tanggal_dikembalikan else None,
                            jumlah_mesin_kembali=jumlah_mesin_kembali,
                            kondisi_mesin=kondisi,
                            keterangan=keterangan
                        )
                        session.add(m)
                        session.commit()
                        session.add(History(mesin_id=m.id, aksi="Tambah"))
                        session.commit()
                        st.success("Mesin berhasil ditambahkan!")
                except Exception as e:
                    st.error(f"Gagal menambahkan mesin: {e}")

    # ---------------------------
    # EDIT/HAPUS MESIN
    # ---------------------------
    elif menu == "Edit/Hapus Mesin":
        if st.session_state["role"] != "admin":
            st.warning("Hanya admin yang bisa mengedit/hapus mesin!")
        else:
            st.subheader("✏️ Edit/Hapus Mesin")
            data = session.query(Mesin).all()
            mesin_list = {m.id: f"{m.kode_mesin} - {m.nama_mesin}" for m in data}
            pilih_id = st.selectbox("Pilih Mesin", list(mesin_list.keys()), format_func=lambda x: mesin_list[x])
            mesin = session.query(Mesin).get(pilih_id)

            if mesin:
                kode = st.text_input("Kode Mesin", mesin.kode_mesin)
                nama = st.text_input("Nama Mesin", mesin.nama_mesin)
                brand = st.text_input("Brand", mesin.brand)
                jumlah_mesin = st.number_input("Jumlah Mesin", min_value=0, value=mesin.jumlah_mesin)
                kondisi = st.selectbox("Kondisi Mesin", ["Baik","Rusak","Maintenance"],
                                       index=["Baik","Rusak","Maintenance"].index(mesin.kondisi_mesin) if mesin.kondisi_mesin else 0)
                keterangan = st.text_area("Keterangan", mesin.keterangan or "")

                if st.button("Update"):
                    mesin.kode_mesin = kode
                    mesin.nama_mesin = nama
                    mesin.brand = brand
                    mesin.jumlah_mesin = jumlah_mesin
                    mesin.kondisi_mesin = kondisi
                    mesin.keterangan = keterangan
                    session.commit()
                    session.add(History(mesin_id=mesin.id, aksi="Update"))
                    session.commit()
                    st.success("Mesin berhasil diupdate!")

                if st.button("Hapus"):
                    session.delete(mesin)
                    session.commit()
                    session.add(History(mesin_id=mesin.id, aksi="Hapus"))
                    session.commit()
                    st.warning("Mesin berhasil dihapus!")

    # ---------------------------
    # UPLOAD EXCEL
    # ---------------------------
    elif menu == "Upload Excel":
        if st.session_state["role"] != "admin":
            st.warning("Hanya admin yang bisa upload Excel!")
        else:
            st.subheader("📤 Upload Data dari Excel")
            uploaded_file = st.file_uploader("Pilih file Excel", type=["xlsx"])
            hapus_sebelumnya = st.checkbox("Hapus semua data sebelumnya sebelum upload")

            if uploaded_file:
                df = pd.read_excel(uploaded_file, header=0)
                df.columns = df.columns.str.strip()
                st.write("Preview data:")
                st.dataframe(df.head())

                if st.button("Simpan ke Database"):
                    if hapus_sebelumnya:
                        session.query(Mesin).delete()
                        session.commit()
                    for _, row in df.iterrows():
                        kode_mesin = str(row.get('Kode Mesin', '')).strip()
                        nama_mesin = str(row.get('Nama Mesin', '')).strip()
                        brand = str(row.get('Brand', '')).strip()
                        jumlah_mesin = int(row.get('Jumlah Mesin', 0))
                        tanggal_pemasukan = parse_tanggal(row.get('Tanggal Pemasukan'))
                        exist = session.query(Mesin).filter_by(kode_mesin=kode_mesin).first()
                        if exist:
                            exist.nama_mesin = nama_mesin
                            exist.brand = brand
                            exist.jumlah_mesin = jumlah_mesin
                            exist.tanggal_pemasukan = tanggal_pemasukan
                            session.commit()
                            session.add(History(mesin_id=exist.id, aksi="Update via Upload Excel"))
                            session.commit()
                        else:
                            m = Mesin(
                                kode_mesin=kode_mesin, nama_mesin=nama_mesin, brand=brand,
                                jumlah_mesin=jumlah_mesin, tanggal_pemasukan=tanggal_pemasukan
                            )
                            session.add(m)
                            session.commit()
                            session.add(History(mesin_id=m.id, aksi="Upload Excel"))
                            session.commit()
                    st.success("Data berhasil diupload ke database!")

    # ---------------------------
    # RIWAYAT
    # ---------------------------
    elif menu == "Riwayat":
        st.subheader("📜 Riwayat Perubahan Data")
        data = session.query(History).all()
        df = pd.DataFrame([(h.id, h.mesin_id, h.aksi, h.waktu) for h in data],
                          columns=["ID", "Mesin ID", "Aksi", "Waktu"])
        st.dataframe(df)

    # ---------------------------
    # TRANSAKSI
    # ---------------------------
    elif menu == "Transaksi":
        st.subheader("💼 Transaksi Mesin")
        sub_menu = st.radio("Pilih Transaksi", ["Sewa", "Kembalikan", "Jual"])
        data_mesin = session.query(Mesin).all()
        mesin_list = {m.id: f"{m.kode_mesin} - {m.nama_mesin} (Stok: {m.jumlah_mesin})" for m in data_mesin}

        pilih_id = st.selectbox("Pilih Mesin", list(mesin_list.keys()), format_func=lambda x: mesin_list[x])
        mesin = session.query(Mesin).get(pilih_id)

        if sub_menu == "Sewa":
            jumlah = st.number_input("Jumlah yang disewa", min_value=0, max_value=mesin.jumlah_mesin, value=0)
            tanggal = st.date_input("Tanggal Sewa", datetime.now())
            if st.button("Proses Sewa"):
                mesin.jumlah_mesin -= jumlah
                mesin.jumlah_sewa = (mesin.jumlah_sewa or 0) + jumlah
                mesin.tanggal_sewa = datetime.combine(tanggal, datetime.min.time())
                session.commit()
                session.add(History(mesin_id=mesin.id, aksi=f"Sewa {jumlah}"))
                session.commit()
                st.success(f"{jumlah} mesin berhasil disewa!")

        elif sub_menu == "Kembalikan":
            jumlah = st.number_input("Jumlah yang dikembalikan", min_value=0, max_value=mesin.jumlah_sewa or 0, value=0)
            tanggal = st.date_input("Tanggal Kembali", datetime.now())
            if st.button("Proses Kembalikan"):
                mesin.jumlah_mesin += jumlah
                mesin.jumlah_mesin_kembali = (mesin.jumlah_mesin_kembali or 0) + jumlah
                mesin.tanggal_dikembalikan = datetime.combine(tanggal, datetime.min.time())
                session.commit()
                session.add(History(mesin_id=mesin.id, aksi=f"Kembali {jumlah}"))
                session.commit()
                st.success(f"{jumlah} mesin berhasil dikembalikan!")

        elif sub_menu == "Jual":
            jumlah = st.number_input("Jumlah yang dijual", min_value=0, max_value=mesin.jumlah_mesin, value=0)
            tanggal = st.date_input("Tanggal Penjualan", datetime.now())
            if st.button("Proses Jual"):
                mesin.jumlah_mesin -= jumlah
                mesin.tanggal_penjualan = datetime.combine(tanggal, datetime.min.time())
                session.commit()
                session.add(History(mesin_id=mesin.id, aksi=f"Jual {jumlah}"))
                session.commit()
                st.success(f"{jumlah} mesin berhasil dijual!")
