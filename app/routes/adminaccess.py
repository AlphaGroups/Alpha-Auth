# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from utils.auth import get_current_user
# from database import get_db
# from models import AdminClassAccess
# from utils.adminVideos import grant_admin_class_access

# router = APIRouter(prefix="/adminaccess", tags=["AdminAccess"])

# def grant_admin_class_access(db: Session, admin_id: int, class_ids: list[int]):
#     for class_id in class_ids:
#         # Check if access already exists
#         existing = db.query(AdminClassAccess).filter_by(admin_id=admin_id, class_id=class_id).first()
#         if not existing:
#             access = AdminClassAccess(admin_id=admin_id, class_id=class_id)
#             db.add(access)
#     db.commit()

# @router.post("/grant")
# def grant_access(admin_id: int, class_ids: list[int], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     if current_user.role != "superadmin":
#         raise HTTPException(status_code=403, detail="Only superadmin can grant access")

#     grant_admin_class_access(db, admin_id, class_ids)
#     return {"message": f"Admin {admin_id} now has access to classes {class_ids}"}


# app/routes/adminaccess.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from utils.auth import get_current_user
from models import Admin, AdminClassAccess, Class  # Class optional but recommended to validate class_ids

router = APIRouter(prefix="/adminaccess", tags=["AdminAccess"])


def _is_superadmin(current_user) -> bool:
    # adapt if current_user.role is Enum: e.g. return current_user.role == RoleEnum.superadmin
    return getattr(current_user, "role", "") == "superadmin"


# ------------------ Helpers ------------------

def grant_admin_class_access(db: Session, admin_id: int, class_ids: list[int]):
    """Idempotent: only create missing AdminClassAccess rows."""
    # optionally validate that the admin exists is done by the caller
    # optionally validate each class exists:
    existing = {
        (a.admin_id, a.class_id) for a in db.query(AdminClassAccess).filter(
            AdminClassAccess.admin_id == admin_id,
            AdminClassAccess.class_id.in_(class_ids)
        )
    }
    for cid in class_ids:
        key = (admin_id, cid)
        if key not in existing:
            db.add(AdminClassAccess(admin_id=admin_id, class_id=cid))
    db.flush()  # push to DB but don't commit here


def revoke_admin_class_access(db: Session, admin_id: int, class_id: int):
    """Revoke single class access; raises 404 if not found."""
    access = db.query(AdminClassAccess).filter_by(admin_id=admin_id, class_id=class_id).first()
    if not access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access not found")
    db.delete(access)
    db.flush()


def revoke_all_admin_access(db: Session, admin_id: int):
    """Remove all class access rows for admin_id (safe delete)."""
    db.query(AdminClassAccess).filter(AdminClassAccess.admin_id == admin_id).delete(synchronize_session=False)
    db.flush()


# ------------------ Routes ------------------

@router.post("/grant", status_code=status.HTTP_200_OK)
def grant_access(
    admin_id: int,
    class_ids: list[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not _is_superadmin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superadmin can grant access")

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # optional: validate class ids exist
    missing_classes = []
    if class_ids:
        found = {c.id for c in db.query(Class).filter(Class.id.in_(class_ids)).all()}
        missing_classes = [cid for cid in class_ids if cid not in found]
        if missing_classes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Some class_ids do not exist", "missing_class_ids": missing_classes}
            )

    try:
        grant_admin_class_access(db, admin_id, class_ids)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while granting access")

    # return current access list for convenience
    accesses = [a.class_id for a in admin.class_accesses]
    return {"message": f"Admin {admin_id} now has access to classes {class_ids}", "current_access": accesses}


@router.delete("/revoke/{admin_id}/class/{class_id}", status_code=status.HTTP_200_OK)
def revoke_access_route(
    admin_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not _is_superadmin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superadmin can revoke access")

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    try:
        revoke_admin_class_access(db, admin_id, class_id)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while revoking access")

    return {"message": f"Revoked access for admin {admin_id} on class {class_id}", "admin": admin_id, "class_id": class_id}


@router.delete("/revoke/{admin_id}/all", status_code=status.HTTP_200_OK)
def revoke_all_access_route(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not _is_superadmin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superadmin can revoke access")

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    try:
        revoke_all_admin_access(db, admin_id)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while revoking all access")

    return {"message": f"All class access removed for admin {admin_id}"}


@router.get("/admin/{admin_id}/classes", status_code=status.HTTP_200_OK)
def get_admin_granted_classes(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get all classes that an admin has access to.
    
    Args:
        admin_id (int): ID of the admin to get classes for
        db (Session): Database session dependency
        current_user: Currently authenticated user (must be superadmin or the admin themselves)
    
    Returns:
        List[dict]: List of class objects that the admin has access to
    """
    # Verify that the current user has permission to view this information
    # Allow access if user is superadmin OR if user is admin and accessing their own data
    is_current_user_admin = getattr(current_user, "role", "") == "admin"
    is_own_data = current_user.id == admin_id
    
    if not _is_superadmin(current_user) and (is_current_user_admin and not is_own_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Get the admin
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    
    # Get all classes the admin has access to through the relationship
    classes = []
    for access in admin.class_accesses:  # This uses the relationship defined in the model
        class_obj = db.query(Class).filter(Class.id == access.class_id).first()
        if class_obj:
            classes.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "access_id": access.id  # ID of the access record
            })
    
    return classes


@router.get("/my-classes", status_code=status.HTTP_200_OK)
def get_my_granted_classes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get all classes that the current admin user has access to.
    
    Args:
        db (Session): Database session dependency
        current_user: Currently authenticated user (must be an admin or superadmin)
    
    Returns:
        List[dict]: List of class objects that the current admin has access to
    """
    # Allow access for both admins and superadmins
    current_role = getattr(current_user, "role", "")
    if current_role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint")
    
    # Get the admin record for the current user
    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin record not found")
    
    # Get all classes the admin has access to through the relationship
    classes = []
    for access in admin.class_accesses:  # This uses the relationship defined in the model
        class_obj = db.query(Class).filter(Class.id == access.class_id).first()
        if class_obj:
            classes.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "access_id": access.id  # ID of the access record
            })
    
    return classes
