from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth_router
from routes.need_routes import need_router
from routes.share_routes import share_router
from routes.announcements import announcements_router
from routes.bucket_routes import bucket_router


# Initialize the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include the routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(need_router, prefix="/food", tags=["Need Food Routes"])
app.include_router(share_router, prefix="/food", tags=["Share Food Routes"])
app.include_router(announcements_router, prefix="/announcements", tags=["Announcements Routes"])
app.include_router(bucket_router, prefix="/storage", tags=["Storage Routes"])


