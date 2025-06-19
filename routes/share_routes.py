from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from uuid import uuid4

from models import ShareFood, Users
from database import get_db
from routes.auth import get_current_user
from pydantic import BaseModel

UPLOAD_DIR = "uploads/share_food"
share_router = APIRouter()

# Pydantic model
class ShareFoodResponseModel(BaseModel):
    id: int
    waktu: str
    tanggal: str
    koordinat: str
    nama_pembagi: str
    nomor_pembagi: str
    nama_kegiatan: str
    nama_makanan: str
    jenis_makanan: str
    jumlah_makanan: int
    keterangan: str
    image_url: Optional[str] = None
    waktu_kadaluwarsa: str
    tipe_makanan: Optional[str] = None
    wadah_makanan: Optional[str] = None
    makanan_diambil: Optional[str] = None
    status: str

    class Config:
        orm_mode = True

# Endpoint untuk berbagi makanan dengan unggahan gambar
@share_router.post("/share", status_code=201)
async def create_share_food_with_image(
    waktu: str = Form(...),
    tanggal: str = Form(...),
    koordinat: str = Form(...),
    nama_pembagi: str = Form(...),
    nomor_pembagi: str = Form(...),
    nama_kegiatan: str = Form(...),
    nama_makanan: str = Form(...),
    jenis_makanan: str = Form(...),
    jumlah_makanan: int = Form(...),
    keterangan: str = Form(...),
    waktu_kadaluwarsa: str = Form(...),
    tipe_makanan: Optional[str] = Form(None),
    wadah_makanan: Optional[str] = Form(None),
    makanan_diambil: Optional[str] = Form(None),
    image: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)  # membuat folder jika belum ada
        file_ext = image.filename.split('.')[-1]
        unique_filename = f"{uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        image_url = f"/{file_path}"  # atau bisa juga URL penuh kalau disajikan lewat static hosting
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

    new_share_food = ShareFood(
        user_id=current_user.id,
        user_name=current_user.name,
        waktu=waktu,
        tanggal=tanggal,
        koordinat=koordinat,
        nama_pembagi=nama_pembagi,
        nomor_pembagi=nomor_pembagi,
        nama_kegiatan=nama_kegiatan,
        nama_makanan=nama_makanan,
        jenis_makanan=jenis_makanan,
        jumlah_makanan=jumlah_makanan,
        keterangan=keterangan,
        waktu_kadaluwarsa=waktu_kadaluwarsa,
        tipe_makanan=tipe_makanan,
        wadah_makanan=wadah_makanan,
        makanan_diambil=makanan_diambil,
        image_url=image_url  # Simpan URL gambar ke database
    )
    
    db.add(new_share_food)
    db.commit()
    db.refresh(new_share_food)
    
    return {"message": "Shared food successfully inserted", "share_food_id": new_share_food.id, "image_url": image_url}


# Get all shareFood entries
@share_router.get("/share", response_model=List[ShareFoodResponseModel], status_code=200)
def get_all_share_foods(db: Session = Depends(get_db)):
    """
    Retrieve all share food requests from the database.
    """
    share_foods = db.query(ShareFood).all()

    if not share_foods:
        raise HTTPException(status_code=404, detail="No food requests found")

    return share_foods

@share_router.delete("/share", status_code=200)
def delete_all_share_foods(
    current_user: Users = Depends(get_current_user),  # Automatically get the current logged-in user
    db: Session = Depends(get_db)
):
    # Find all shareFood entries associated with the logged-in user
    share_foods = db.query(ShareFood).filter(ShareFood.user_id == current_user.id).all()

    # If no entries are found, raise 404
    if not share_foods:
        raise HTTPException(status_code=404, detail="No food share found for this user")

    # Delete all found shareFood entries
    for share_food in share_foods:
        db.delete(share_food)
    
    db.commit()

    return {"message": "All food requests successfully deleted"}

# Accept shareFood request
@share_router.post("/share/accept/{share_food_id}", status_code=200)
def accept_share_food(
    share_food_id: int, 
    db: Session = Depends(get_db)
):
    # Cari entri makanan yang akan dibagikan berdasarkan ID
    share_food = db.query(ShareFood).filter(ShareFood.id == share_food_id).first()

    # Jika tidak ditemukan, kembalikan error 404
    if not share_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Ubah status menjadi Accepted
    share_food.status = "Accepted"
    db.commit()
    db.refresh(share_food)

    return {
        "message": "Food request successfully accepted",
        "share_food": {
            "id": share_food.id,
            "nama_kegiatan": share_food.nama_kegiatan,
            "nama_makanan": share_food.nama_makanan,
            "jenis_makanan": share_food.jenis_makanan,
            "wadah_makanan": share_food.wadah_makanan,
            "makanan_diambil": share_food.makanan_diambil,
            "waktu": share_food.waktu,
            "tanggal": share_food.tanggal,
            "jumlah_makanan": share_food.jumlah_makanan,
            "nama_pembagi": share_food.nama_pembagi,
            "nomor_pembagi": share_food.nomor_pembagi,
            "keterangan": share_food.keterangan,
            "waktu_kadaluwarsa": share_food.waktu_kadaluwarsa,
            "koordinat": share_food.koordinat,  # Pastikan ini tersimpan dalam format lat,lng
            "status": share_food.status,
            "image_url": share_food.image_url,  # Jika ada gambar makanan
        }
    }


# Reject shareFood request
@share_router.post("/share/reject/{share_food_id}", status_code=200)
def reject_share_food(
    share_food_id: int, 
    db: Session = Depends(get_db)
):
    # Find the shareFood entry by id
    share_food = db.query(ShareFood).filter(ShareFood.id == share_food_id).first()

    # If no entry is found, raise 404
    if not share_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Change the status to Rejected
    share_food.status = "Rejected"
    db.commit()

    return {"message": "Food request is rejected", "share_food_id": share_food.id}

@share_router.delete("/share/{share_food_id}", status_code=200)
def delete_share_food(
    share_food_id: int, 
    # current_user: Users = Depends(get_current_user),  # Automatically get current logged-in user
    db: Session = Depends(get_db)
):
    # Find the shareFood entry by id
    share_food = db.query(ShareFood).filter(ShareFood.id == share_food_id).first()

    # If no entry is found, raise 404
    if not share_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Check if the current user is the one who created the request
    # if share_food.user_name != current_user.name:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this food request")
    
    # Delete the found shareFood entry
    db.delete(share_food)
    db.commit()

    return {"message": f"Food request with ID {share_food_id} successfully deleted"}