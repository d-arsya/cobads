from pydantic import BaseModel

# Token response model for login
class TokenResponseModel(BaseModel):
    access_token: str
    token_type: str
    username: str

# User signup request model
class UserSignupModel(BaseModel):
    name: str
    email: str
    phone: str
    password: str
