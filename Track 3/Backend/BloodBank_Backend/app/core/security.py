from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import string

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    """Security utilities for password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generate password hash using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        Generate a random secure password
        
        Args:
            length: Password length (default: 12)
            
        Returns:
            Random password string
        """
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate a secure reset token
        
        Returns:
            Random token string
        """
        return secrets.token_urlsafe(32)
