
from sqlalchemy.orm import Session
from models import AdminClassAccess  # <-- use the class, not 'admin_class_access'


def grant_admin_class_access(db: Session, admin_id: int, class_ids: list[int]):
    # Remove old access
    db.execute(
        AdminClassAccess.delete().where(AdminClassAccess.c.admin_id == admin_id)
    )

    # Add new access
    for class_id in class_ids:
        db.execute(
            AdminClassAccess.insert().values(admin_id=admin_id, class_id=class_id)
        )
    db.commit()
