from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from models import NeedFood, Users
from database import get_db
from routes.auth import get_current_user
from pydantic import BaseModel


# Pydantic model for request validation
class NeedFoodCreateModel(BaseModel):
    waktu: str
    tanggal: str
    koordinat: str
    nama_pencari: str
    nomor_pencari: str
    nama_kegiatan: str
    nama_tempat: str
    jumlah_makanan: int
    keterangan: str

# Pydantic model for response
class NeedFoodResponseModel(BaseModel):
    id: int
    user_id: int
    user_name: str
    waktu: str
    tanggal: str
    koordinat: str
    nama_pencari: str
    nomor_pencari: str
    nama_kegiatan: str
    nama_tempat: str
    jumlah_makanan: int
    keterangan: str
    status: str

    class Config:
        orm_mode = True  # Allows returning SQLAlchemy models as Pydantic models

# Food router
need_router = APIRouter()

# Create NeedFood entry - now gets user info from the logged-in user
@need_router.post("/need", status_code=201)
def create_need_food(
    need_food_data: NeedFoodCreateModel, 
    current_user: Users = Depends(get_current_user),  # Automatically get current logged-in user
    db: Session = Depends(get_db)
):
    # Use current_user info from the token
    user_id = current_user.id
    user_name = current_user.name

    # Create new need_food entry with the foreign key relationship
    new_need_food = NeedFood(
        user_id=user_id,
        user_name=user_name,
        waktu=need_food_data.waktu,
        tanggal=need_food_data.tanggal,
        koordinat=need_food_data.koordinat,
        nama_pencari=need_food_data.nama_pencari,
        nomor_pencari=need_food_data.nomor_pencari,
        nama_kegiatan=need_food_data.nama_kegiatan, 
        nama_tempat=need_food_data.nama_tempat,
        jumlah_makanan=need_food_data.jumlah_makanan,
        keterangan=need_food_data.keterangan
    )
    
    db.add(new_need_food)
    db.commit()
    db.refresh(new_need_food)
    
    return {"message": "Data successfully inserted", "need_food_id": new_need_food.id}

# Get all NeedFood entries
@need_router.get("/need", response_model=List[NeedFoodResponseModel], status_code=200)
def get_all_need_foods(db: Session = Depends(get_db)):
    """
    Retrieve all need food requests from the database.
    """
    need_foods = db.query(NeedFood).all()
    
    if not need_foods:
        raise HTTPException(status_code=404, detail="No food requests found")

    return need_foods

@need_router.delete("/need", status_code=200)
def delete_all_need_foods(
    current_user: Users = Depends(get_current_user),  # Automatically get the current logged-in user
    db: Session = Depends(get_db)
):
    # Find all NeedFood entries associated with the logged-in user
    need_foods = db.query(NeedFood).filter(NeedFood.user_id == current_user.id).all()

    # If no entries are found, raise 404
    if not need_foods:
        raise HTTPException(status_code=404, detail="No food requests found for this user")

    # Delete all found NeedFood entries
    for need_food in need_foods:
        db.delete(need_food)
    
    db.commit()

    return {"message": "All food requests successfully deleted"}


@need_router.post("/need/accept/{need_food_id}", status_code=200)
def accept_need_food(
    need_food_id: int, 
    # current_user: Users = Depends(get_current_user),  # Automatically get current logged-in user
    db: Session = Depends(get_db)
):
    # Find the NeedFood entry by id
    need_food = db.query(NeedFood).filter(NeedFood.id == need_food_id).first()

    # If no entry is found, raise 404
    if not need_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Check if the current user is the one who created the request
    # if need_food.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to accept this food request")

    # Change the status to Accepted
    need_food.status = "Accepted"
    db.commit()

    return {"message": "Food request successfully accepted", "need_food_id": need_food.id}

@need_router.post("/need/reject/{need_food_id}", status_code=200)
def accept_need_food(
    need_food_id: int, 
    # current_user: Users = Depends(get_current_user),  # Automatically get current logged-in user
    db: Session = Depends(get_db)
):
    # Find the NeedFood entry by id
    need_food = db.query(NeedFood).filter(NeedFood.id == need_food_id).first()

    # If no entry is found, raise 404
    if not need_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Check if the current user is the one who created the request
    # if need_food.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to accept this food request")

    # Change the status to Accepted
    need_food.status = "Rejected"
    db.commit()

    return {"message": "Food request is rejected", "need_food_id": need_food.id}

@need_router.delete("/need/{need_food_id}", status_code=200)
def delete_need_food(
    need_food_id: int, 
    # current_user: Users = Depends(get_current_user),  # Automatically get current logged-in user
    db: Session = Depends(get_db)
):
    # Find the NeedFood entry by id
    need_food = db.query(NeedFood).filter(NeedFood.id == need_food_id).first()

    # If no entry is found, raise 404
    if not need_food:
        raise HTTPException(status_code=404, detail="Food request not found")

    # Check if the current user is the one who created the request
    # if need_food.user_name != current_user.name:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this food request")
    
    # Delete the found NeedFood entry
    db.delete(need_food)
    db.commit()

    return {"message": f"Food request with ID {need_food_id} successfully deleted"}


