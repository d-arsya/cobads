from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models import Announcement
from database import get_db  

class AnnouncementBase(BaseModel):
    title: str
    description: str


class AnnouncementUpdate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int

    class Config:
        orm_mode = True  # Allows returning SQLAlchemy models as Pydantic models

# Initialize the APIRouter for announcements
announcements_router = APIRouter()

# Create an announcement (POST)
@announcements_router.post("", response_model=AnnouncementResponse, status_code=201)
def create_announcement(
    announcement: AnnouncementBase, db: Session = Depends(get_db)
):
    db_announcement = Announcement(
        title=announcement.title,
        description=announcement.description,

    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

# Get all announcements (GET)
@announcements_router.get("", response_model=list[AnnouncementResponse], status_code=200)
def get_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).all()
    return announcements

# Get a specific announcement by ID (GET)
@announcements_router.get("/{announcement_id}", response_model=AnnouncementResponse, status_code=200)
def get_announcement(
    announcement_id: int, db: Session = Depends(get_db)
):
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return db_announcement

# Update an announcement by ID (PUT)
@announcements_router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int, announcement_data: AnnouncementUpdate, db: Session = Depends(get_db)
):
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Update the fields
    db_announcement.title = announcement_data.title
    db_announcement.description = announcement_data.description

    db.commit()
    db.refresh(db_announcement)
    return db_announcement

# Delete an announcement by ID (DELETE)
@announcements_router.delete("/{announcement_id}", status_code=204)
def delete_announcement(
    announcement_id: int, db: Session = Depends(get_db)
):
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")

    db.delete(db_announcement)
    db.commit()
    return {"message": "Announcement deleted successfully"}