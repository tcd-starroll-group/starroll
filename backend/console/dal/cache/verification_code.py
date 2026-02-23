"""Verification code DAL operations."""

import random
from typing import Optional
from backend.console.dal.cache.client import RedisClient
from backend.config.settings import Settings


class VerificationCodeDAO:
    """Data Access Object for verification code operations."""
    
    def __init__(self, settings: Settings):
        """Initialize with Redis client.
        
        Args:
            settings: Settings object containing Redis configuration
        """
        self.redis_client = RedisClient.get_instance(settings)
        self.code_expire_seconds: int = 600  # 验证码有效期10分钟
        self.key_prefix: str = "verification_code:"
    
    def _get_key(self, target: str) -> str:
        """Generate Redis key for verification code.
        
        Args:
            target: Email or identifier for verification
            
        Returns:
            Redis key
        """
        return f"{self.key_prefix}{target}"
    
    def generate_code(self, length: int = 6) -> str:
        """Generate a random verification code.
        
        Args:
            length: Length of the code (default: 6)
            
        Returns:
            Generated verification code
        """
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    def save_code(self, target: str, code: Optional[str] = None) -> str:
        """Save verification code to Redis.
        
        Args:
            target: Email or identifier for verification
            code: Verification code (optional, will be generated if not provided)
            
        Returns:
            The verification code
        """
        if code is None:
            code = self.generate_code()
        
        key = self._get_key(target)
        self.redis_client.set(key, code, ex=self.code_expire_seconds)
        return code
    
    def verify_code(self, target: str, code: str) -> bool:
        """Verify and consume verification code.
        
        Args:
            target: Email or identifier for verification
            code: Code to verify
            
        Returns:
            True if code is valid and matches, False otherwise
        """
        key = self._get_key(target)
        stored_code = self.redis_client.get(key)
        
        # If key doesn't exist (expired or not set)
        if stored_code is None:
            return False
        
        # Check if code matches
        if stored_code == code:
            # Delete after successful verification (one-time use)
            self.redis_client.delete(key)
            return True
        return False
    
    def get_code(self, target: str) -> Optional[str]:
        """Get verification code without consuming it.
        
        Args:
            target: Email or identifier for verification
            
        Returns:
            Verification code or None if not found or expired
        """
        key = self._get_key(target)
        return self.redis_client.get(key)
    
    def delete_code(self, target: str) -> int:
        """Delete verification code.
        
        Args:
            target: Email or identifier for verification
            
        Returns:
            Number of keys deleted (0 or 1)
        """
        key = self._get_key(target)
        return self.redis_client.delete(key)
