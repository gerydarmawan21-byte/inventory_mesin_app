from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Path database di folder data
DB_PATH = "data/inventory.db"
os.makedirs("data", exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # admin/user

class Mesin(Base):
    __tablename__ = "mesin"
    id = Column(Integer, primary_key=True)
    kode_mesin = Column(String, unique=True)
    nama_mesin = Column(String)
    brand = Column(String)
    sg = Column(String)
    nomor_dokumen = Column(String)
    jumlah_mesin = Column(Integer, default=0)
    harga_mesin = Column(Float, default=0.0)
    tanggal_pemasukan = Column(DateTime)
    tanggal_penjualan = Column(DateTime, nullable=True)
    tanggal_sewa = Column(DateTime, nullable=True)
    jumlah_sewa = Column(Integer, default=0)
    tanggal_dikembalikan = Column(DateTime, nullable=True)
    jumlah_mesin_kembali = Column(Integer, default=0)
    kondisi_mesin = Column(String, default="Baik")
    keterangan = Column(String, nullable=True)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    mesin_id = Column(Integer)
    aksi = Column(String)
    waktu = Column(DateTime, default=datetime.now)

# Buat table jika belum ada
Base.metadata.create_all(engine)

# Buat admin default jika belum ada
if not session.query(User).filter_by(username="admin").first():
    admin_user = User(username="admin", password="admin123", role="admin")
    session.add(admin_user)
    session.commit()
