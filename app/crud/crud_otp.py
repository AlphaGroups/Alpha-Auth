from sqlalchemy.orm import Session
from models import OTP
from datetime import datetime, timedelta


def create_otp(db: Session, email: str, otp_code: str, valid_duration: int = 10):
    """
    Create a new OTP record with expiration time
    """
    expiration_time = datetime.utcnow() + timedelta(minutes=valid_duration)
    
    new_otp = OTP(
        email=email,
        otp_code=otp_code,
        expires_at=expiration_time
    )
    
    # Remove any existing OTP records for this email
    db.query(OTP).filter(OTP.email == email).delete()
    
    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)
    
    return new_otp


def get_otp_by_email_and_code(db: Session, email: str, otp_code: str):
    """
    Retrieve OTP record by email and code
    """
    return db.query(OTP).filter(
        OTP.email == email,
        OTP.otp_code == otp_code,
        OTP.expires_at > datetime.utcnow()
    ).first()


def delete_otp(db: Session, email: str):
    """
    Delete OTP record for a specific email
    """
    otp_record = db.query(OTP).filter(OTP.email == email).first()
    if otp_record:
        db.delete(otp_record)
        db.commit()