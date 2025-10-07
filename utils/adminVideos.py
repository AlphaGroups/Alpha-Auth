
from sqlalchemy.orm import Session
from models import AdminClassAccess


def grant_admin_class_access(db: Session, admin_id: int, class_ids: list[int]):
    # Remove old access for this admin
    db.query(AdminClassAccess).filter(AdminClassAccess.admin_id == admin_id).delete(synchronize_session=False)
    
    # Add new access
    for class_id in class_ids:
        access = AdminClassAccess(admin_id=admin_id, class_id=class_id)
        db.add(access)
    db.commit()
