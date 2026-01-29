import jwt
import datetime
from backend.console.dal.rds.client import JWT_SECRET, JWT_ALGORITHM

def create_access_token(data: dict):
    """Generate a new JWT access token"""
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt