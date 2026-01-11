import hashlib
import uuid
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from storage_utils import create_data, load_data_db_table,delete_data, get_item_db, create_data
from session_manager import add_session,get_session
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse
from argon2 import PasswordHasher

# ===============================
# SYSTEM USER SETUP
# ===============================
system_user = {
    "id": "0",
    "username": "system",
    "role": "ADMIN",       # admin voor toegang tot alles
    "hotel_guest": False,
    "active": True,
    "created_at": datetime.now().strftime("%Y-%m-%d")
}

system_token = "system-token"

# Voeg system user toe aan session manager als hij nog niet bestaat
if not get_session(system_token):
    add_session(system_token, system_user)


# ===============================
# UserService Class
# ===============================
class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2 and md5"""
        # ph = PasswordHasher()
        # return ph.hash(hashlib.md5(password.encode()).hexdigest())
        return hashlib.md5(password.encode()).hexdigest()
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if username already exists"""
        users = load_data_db_table("users")
        return any(user.get('username') == username for user in users)
    
    @staticmethod
    def create_user(user_data: UserRegister) -> MessageResponse:
        """Create a new user account"""
        # Check if username already exists
        if UserService.user_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = UserService.hash_password(user_data.password)
                
        # Create new user with extended fields
        new_user = {
            'username': user_data.username,
            'password': hashed_password,
            'name': user_data.name,
            'email': user_data.email,
            'phone': user_data.phone,
            'role': 'USER',
            'created_at': datetime.now().strftime("%Y-%m-%d"),
            'birth_year': user_data.birth_year,
            'active': True
        }
        
        create_data("users", new_user)
        
        return MessageResponse(message="User created successfully")
    
    @staticmethod
    def create_hotel_guest(user_data: UserRegister) -> MessageResponse:
        """Create a hotel guest user with free parking privileges"""
        # Zet hotel_guest flag
        guest_data = user_data.dict()
        guest_data["role"] = "USER"
        guest_data["hotel_guest"] = True
        return UserService.create_user(UserRegister(**guest_data))

    def delete_user(user_id: str) -> MessageResponse:
        """Delete a user by ID"""
        delete_data(id,"users")
        
        return MessageResponse(message="User deleted successfully")
    
    @staticmethod
    def update_user(user_id: str, user_data: UserRegister) -> MessageResponse:
        """Update user information"""
        users = load_data_db_table("users")
        user_found = False
        
        for user in users:
            if user.get('id') == user_id:
                user_found = True
                user['name'] = user_data.name
                user['email'] = user_data.email
                user['phone'] = user_data.phone
                user['birth_year'] = user_data.birth_year
                if user_data.password:
                    user['password'] = UserService.hash_password(user_data.password)
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        save_user_data(users)
        return MessageResponse(message="User updated successfully")
    
    @staticmethod
    def authenticate_user(credentials: UserLogin) -> LoginResponse:
        """Authenticate user and create session"""
        # Validate credentials
        if not credentials.username or not credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing credentials"
            )
        
        # Hash provided password
        hashed_password = UserService.hash_password(credentials.password)
        
        # Load users and find match
        users = load_data_db_table("users")
        
        for user in users:
            if (user.get("username") == credentials.username and 
                user.get("password") == hashed_password):
                
                # Generate session token
                token = str(uuid.uuid4())
                add_session(token, user)
                
                return LoginResponse(
                    message="User logged in successfully",
                    session_token=token
                )
        
        # No matching user found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """Get user by username (without password)"""
        user = get_item_db("username",username,"users")[0]
        if user :
            return {
                        'id': user.get('id'),
                        'username': user.get('username'),
                        'name': user.get('name'),
                        'email': user.get('email'),
                        'phone': user.get('phone'),
                        'role': user.get('role', 'USER'),
                        'created_at': user.get('created_at'),
                        'birth_year': user.get('birth_year'),
                        'active': user.get('active', True)
                    }
        return None
    
    @staticmethod
    def update_user(user_data: UserRegister) -> MessageResponse:
        """Update existing user details"""
        users = load_data_db_table("users")
        for user in users:
            if user.get("username") == user_data.username:
                user['name'] = user_data.name
                user['email'] = user_data.email
                user['phone'] = user_data.phone
                user['birth_year'] = user_data.birth_year
                save_user_data(users)
                return MessageResponse(message="User updated successfully")
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    @staticmethod
    def delete_user(username: str) -> MessageResponse:
        """Delete user by username"""
        users = load_data_db_table("users")
        for i, user in enumerate(users):
            if user.get("username") == username:
                users.pop(i)
                delete_data(user['id'], 'id', 'users')
                return MessageResponse(message="User deleted successfully")
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    @staticmethod
    def read_user(username: str) -> Optional[dict]:
        """Read user details by username"""
        return UserService.get_user_by_username(username)
    
    @staticmethod
    def get_system_user_token() -> str:
        """Return the system token for automatic actions"""
        return system_token