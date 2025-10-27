from fastapi import HTTPException, status
from session_manager import get_session
from typing import Dict, Any
class ValidationService:
     @staticmethod
     def validate_session_token(token: str) -> Dict[str, Any]:
        """Validate session token and return user data"""
        if not token:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized: Missing session token"
            )
            
        session_user = get_session(token)
        if not session_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized: Invalid session token"
                )
            
        return session_user
     @staticmethod
     def validate_admin_access(user: Dict[str, Any]):
        """Check if user has admin access"""
        if user.get('role') != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin privileges required"
            )
     @staticmethod
     def check_valid_admin(user: Dict[str, Any]):
        """Return true or false if the user is an Admin"""
        if user.get('role') != 'ADMIN':
            return True
        return False 
     
     
     
        