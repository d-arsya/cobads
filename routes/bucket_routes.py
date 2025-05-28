from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import boto3
import os
from botocore.exceptions import BotoCoreError, NoCredentialsError, PartialCredentialsError, EndpointConnectionError
from database import get_db
from routes.auth import get_current_user
from sqlalchemy.orm import Session
from models import Users

bucket_router = APIRouter()

# Ambil variabel lingkungan
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Pastikan semua variabel lingkungan terisi
if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, BUCKET_NAME]):
    raise ValueError("Missing AWS configuration. Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, and BUCKET_NAME.")

# Inisialisasi klien boto3
try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
except (NoCredentialsError, PartialCredentialsError) as e:
    raise ValueError(f"AWS credentials error: {str(e)}")

@bucket_router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), 
    current_user: Users = Depends(get_current_user),  # Otentikasi pengguna
    db: Session = Depends(get_db)
):
    try:
        # Upload ke S3 tanpa ACL (gunakan ContentType agar bisa dibuka langsung di browser)
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        # URL publik dari file (pastikan bucket sudah diatur agar objek dapat diakses publik)
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"
        
        return {"message": "File uploaded successfully", "filename": file.filename, "url": file_url}
    
    except EndpointConnectionError as e:
        raise HTTPException(status_code=500, detail=f"S3 connection error: {str(e)}")
    
    except BotoCoreError as e:
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@bucket_router.get("/storage/{filename}")
async def get_file_url(filename: str, current_user: Users = Depends(get_current_user)):
    try:
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return {"filename": filename, "url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file URL: {str(e)}")
