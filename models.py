from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)

    # Define the relationship with need_food (specifying foreign key)
    need_foods = relationship("NeedFood", back_populates="user", foreign_keys="[NeedFood.user_id]") 
    share_foods = relationship("ShareFood", back_populates="user", foreign_keys="[ShareFood.user_id]")  # Specify which foreign key to use


class NeedFood(Base):
    __tablename__ = "need_food"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_name = Column(String, ForeignKey('users.name'))  
    tanggal = Column(String)
    waktu = Column(String)
    koordinat = Column(String)
    nama_pencari = Column(String)
    nomor_pencari = Column(String)
    nama_kegiatan = Column(String)
    nama_tempat = Column(String)
    jumlah_makanan = Column(Integer)
    keterangan = Column(String)
    status = Column(Enum("Pending", "Accepted", "Rejected", name="status_enum"), default="Pending")  # Status field
    
    # Define relationship (specifying foreign key)
    user = relationship("Users", back_populates="need_foods", foreign_keys=[user_id])  # Specify which foreign key to use
    


class ShareFood(Base):
    __tablename__ = "share_food"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_name = Column(String, ForeignKey('users.name'))  
    
    # Define relationship (specifying foreign key)
    user = relationship("Users", back_populates="share_foods", foreign_keys=[user_id])  # Specify which foreign key to use
    
    # Other columns
    tanggal = Column(String)
    waktu = Column(String)
    koordinat = Column(String)
    nama_pembagi = Column(String)
    nomor_pembagi = Column(String)
    nama_kegiatan = Column(String)
    nama_makanan = Column(String)
    jenis_makanan = Column(String)
    jumlah_makanan = Column(Integer)
    keterangan = Column(String)
    waktu_kadaluwarsa = Column(String)
    tanggal_kadaluwarsa = Column(String)
    tipe_makanan = Column(String)
    wadah_makanan = Column(String)
    makanan_diambil = Column(String)
    status = Column(Enum("Pending", "Accepted", "Rejected", name="status_enum"), default="Pending")
    image_url = Column(String, nullable=True)
    
class Announcement(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)