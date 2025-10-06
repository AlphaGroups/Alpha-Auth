from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "your_secret_key"
RESET_PASSWORD_SALT = "reset-password-salt"

def generate_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=RESET_PASSWORD_SALT)

def verify_reset_token(token: str, expiration: int = 3600) -> str | None:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        return serializer.loads(token, salt=RESET_PASSWORD_SALT, max_age=expiration)
    except Exception:
        return None
