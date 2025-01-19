import uuid
from datetime import datetime, timedelta
import os
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import bcrypt
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365

class User(BaseModel):
    email: EmailStr
    phone: str
    password: str
    tiktok_ids: List[str] = ()
    role: str = 'user'

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    phone: str
    tiktok_ids: List
    role: str
    subscription_expired_at: datetime = None
    created_at: datetime

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    phone: str
    tiktok_ids: List[str] = ()
    subscription_expired_at: datetime = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    token: str
    token_type: str

class UserUpdateRequest(BaseModel):
    phone: Optional[str] = None
    tiktok_ids: Optional[List[str]] = None

class AdminUpdateUserRequest(BaseModel):
    phone: Optional[str] = None
    tiktok_ids: Optional[List[str]] = None
    subscription_expired_at: Optional[datetime] = None

def get_password_hash(password):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash

def verify_password(plain_password, hashed_password):
    userBytes = plain_password.encode('utf-8')
    result = bcrypt.checkpw(userBytes, hashed_password)
    return result

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])