"""Verification code storage utility (for forgot password, registration, etc.)"""
from typing import Optional

from backend.config import settings
from backend.console.dal.cache import VerificationCodeDAO


class VerificationCodeStore:
    """Verification code storage class (uses DAL layer for Redis operations)"""
    def __init__(self):
        # Use verification code operation class from DAL layer
        self.dao = VerificationCodeDAO(settings)

    def generate_verification_code(self, length: int = 6) -> str:
        """Generate 6-digit numeric verification code"""
        return self.dao.generate_code(length)

    def save_verification_code(self, target: str, code: Optional[str] = None) -> str:
        """Save verification code to Redis, return generated verification code"""
        return self.dao.save_code(target, code)

    def verify_verification_code(self, target: str, code: str) -> bool:
        """Verify if verification code is valid (delete after successful verification for one-time use)"""
        return self.dao.verify_code(target, code)


# Global singleton instance (Core requirement: must be defined at file top level with exact naming)
verification_code_store = VerificationCodeStore()