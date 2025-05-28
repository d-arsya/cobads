import os
import bcrypt
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel

from models import Users
from database import get_db  # You should define this function to get a DB session
from dto import TokenResponseModel, UserSignupModel  # Define DTO classes


# OAuth2PasswordBearer for token authentication
oauth2_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Function to generate JWT token
def __generate_token(data: dict) -> str:
    to_encode = data.copy()
    token = jwt.encode(to_encode, os.getenv("SECRET"), algorithm=os.getenv("ALGORITHM"))
    return token

# Function to validate password (hash check)
def __validate_password(password: str, true_password: str) -> bool:
    b_password = password.encode(encoding='utf-8')
    return bcrypt.checkpw(b_password, bytes(true_password, encoding='utf-8'))

# Function to validate JWT token and extract user information
def get_current_user(token: str = Depends(oauth2_token_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET"), algorithms=[os.getenv("ALGORITHM")])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found in token")
        
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user  # Return the user object

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")

# Authentication router
auth_router = APIRouter(tags=['Authentication'])

# Login endpoint
# Login endpoint (Make sure this is inside the router)
@auth_router.post("/login", response_model=TokenResponseModel, status_code=status.HTTP_200_OK)
def user_login(
    auth_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenResponseModel:
    user = db.query(Users).filter((Users.email == auth_data.username) | (Users.name == auth_data.username)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if not __validate_password(auth_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong username or password",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    token = __generate_token(data={"id": str(user.id)})

    return TokenResponseModel(
        access_token=token,
        token_type="Bearer",
        username=user.name
    )

# Signup endpoint
@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignupModel, db: Session = Depends(get_db)):
    # Check if email or username is already in use
    existing_user = db.query(Users).filter(
        (Users.email == user_data.email) | (Users.name == user_data.name)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already in use."
        )

    # Hash the password before saving it to the database
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new user
    new_user = Users(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully!", "user_id": new_user.id}
