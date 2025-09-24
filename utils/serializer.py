# utils/serializer.py
from fastapi import HTTPException
from models import User, Student

def serialize_user(user) -> dict:
    """
    Serialize User or Student object for API response
    """
    if isinstance(user, User):
        first_name = user.first_name or (user.name.split()[0] if user.name else None)
        last_name = user.last_name or (user.name.split()[1] if user.name and len(user.name.split()) > 1 else None)
        return {
            "id": user.id,
            "name": user.name,
            "first_name": first_name,
            "last_name": last_name,
            "email": user.email,
            "role": user.role.value,
            "mobile": str(user.mobile) if user.mobile else None,
        }
    elif isinstance(user, Student):
        return {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": "student",
            "mobile": str(user.mobile) if user.mobile else None,
        }
    else:
        raise HTTPException(status_code=500, detail="Unknown user type")
