import hashlib
import uuid
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from storage_utils import load_json, save_user_data
from session_manager import add_session
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using MD5 (consider using bcrypt for production)"""
        return hashlib.md5(password.encode()).hexdigest()
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if username already exists"""
        users = load_json('data/users.json')
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
        
        # Load existing users
        users = load_json('data/users.json')
        
        # Generate new user ID
        new_id = str(len(users) + 1)
        
        # Create new user with extended fields
        new_user = {
            'id': new_id,
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
        
        # Add to users list and save
        users.append(new_user)
        save_user_data(users)
        
        return MessageResponse(message="User created successfully")
    
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
        users = load_json('data/users.json')
        
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
        users = load_json('data/users.json')
        for user in users:
            if user.get("username") == username:
                # Return user without password for security
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