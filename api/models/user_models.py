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

class User(BaseModel):
    username: str
    name: str
    # Note: password not included in response model for security