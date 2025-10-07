import random
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP code with specified length (default 6 digits)
    """
    return ''.join(random.choices(string.digits, k=length))


def is_otp_valid(otp_code: str, expiration_time: datetime, valid_duration: int = 10) -> bool:
    """
    Check if the OTP is still valid based on expiration time
    Default validity is 10 minutes
    """
    if not otp_code or not expiration_time:
        return False
    
    current_time = datetime.utcnow()
    time_diff = current_time - expiration_time
    return time_diff.total_seconds() < (valid_duration * 60)  # Convert minutes to seconds