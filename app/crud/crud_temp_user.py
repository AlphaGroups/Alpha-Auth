from sqlalchemy.orm import Session
from models import TempUser, User
from datetime import datetime, timedelta
from utils.security import hash_password


def create_temp_user(db: Session, name: str, email: str, password: str, valid_duration: int = 60):
    """
    Create a temporary user record that expires after valid_duration minutes
    """
    # Check if user already exists in main users table
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Check if user already exists in temp table (replace)
    existing_temp_user = db.query(TempUser).filter(TempUser.email == email).first()
    if existing_temp_user:
        db.delete(existing_temp_user)
        db.commit()
    
    expiration_time = datetime.utcnow() + timedelta(minutes=valid_duration)
    hashed_password = hash_password(password)
    
    new_temp_user = TempUser(
        name=name,
        email=email,
        hashed_password=hashed_password,
        expires_at=expiration_time
    )
    
    db.add(new_temp_user)
    db.commit()
    db.refresh(new_temp_user)
    
    return new_temp_user


def get_temp_user_by_email(db: Session, email: str):
    """
    Retrieve a temporary user by email if not expired
    """
    return db.query(TempUser).filter(
        TempUser.email == email,
        TempUser.expires_at > datetime.utcnow()
    ).first()


def delete_temp_user(db: Session, email: str):
    """
    Delete a temporary user by email
    """
    temp_user = db.query(TempUser).filter(TempUser.email == email).first()
    if temp_user:
        db.delete(temp_user)
        db.commit()


def move_temp_user_to_main(db: Session, email: str):
    """
    Move a temporary user to the main user table after verification
    """
    temp_user = get_temp_user_by_email(db, email)
    if not temp_user:
        raise ValueError("Temporary user not found or expired")
    
    # Create main user from temp user
    new_user = User(
        name=temp_user.name,
        email=temp_user.email,
        hashed_password=temp_user.hashed_password,
        is_verified=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Delete the temporary user record
    delete_temp_user(db, email)
    
    return new_user


def cleanup_expired_temp_users(db: Session):
    """
    Delete all expired temporary user records
    """
    expired_temp_users = db.query(TempUser).filter(
        TempUser.expires_at < datetime.utcnow()
    ).all()
    
    for temp_user in expired_temp_users:
        db.delete(temp_user)
    
    db.commit()