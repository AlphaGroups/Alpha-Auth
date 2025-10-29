# from itsdangerous import URLSafeTimedSerializer

# SECRET_KEY = "your_secret_key"
# RESET_PASSWORD_SALT = "reset-password-salt"

# def generate_reset_token(email: str) -> str:
#     serializer = URLSafeTimedSerializer(SECRET_KEY)
#     return serializer.dumps(email, salt=RESET_PASSWORD_SALT)

# def verify_reset_token(token: str, expiration: int = 3600) -> str | None:
#     serializer = URLSafeTimedSerializer(SECRET_KEY)
#     try:
#         return serializer.loads(token, salt=RESET_PASSWORD_SALT, max_age=expiration)
#     except Exception:
#         return None


# utils/token.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

def create_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(seconds=expires_delta)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
