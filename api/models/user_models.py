from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    session_token: str

class MessageResponse(BaseModel):
    message: str

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    session_token: str

class MessageResponse(BaseModel):
    message: str

class User(BaseModel):
    id: Optional[str] = None
    username: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "USER"
    created_at: Optional[str] = None  # Using string to match your date format
    birth_year: Optional[int] = None
    active: Optional[bool] = True
    hotel_guest: Optional[bool] = False
    # Note: password not included in response model for security

class UserFull(BaseModel):
    """Full user model including password hash for internal use"""
    id: Optional[str] = None
    username: str
    password: str  # This will be the hashed password
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "USER"
    created_at: Optional[str] = None
    birth_year: Optional[int] = None
    active: Optional[bool] = True