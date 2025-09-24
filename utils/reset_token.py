# auth/reset_token.py
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ISSUER = os.getenv("JWT_ISSUER")

RESET_PASSWORD_SALT = "reset-password-salt"

def create_reset_token(data: dict, expires_minutes: int = 30):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    data.update({"exp": expire, "iss": ISSUER})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def generate_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=RESET_PASSWORD_SALT)

def verify_reset_token(token: str, expiration: int = 3600) -> str | None:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        return serializer.loads(token, salt=RESET_PASSWORD_SALT, max_age=expiration)
    except Exception:
        return None