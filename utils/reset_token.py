# auth/reset_token.py
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ISSUER = os.getenv("JWT_ISSUER")

def create_reset_token(data: dict, expires_minutes: int = 30):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    data.update({"exp": expire, "iss": ISSUER})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
