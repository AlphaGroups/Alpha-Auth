# utils/rbac.py
from fastapi import Depends, HTTPException, status
from utils.auth import get_current_user

# Role hierarchy
role_hierarchy = {
    "superadmin": ["admin", "teacher", "student"],
    "admin": ["teacher", "student"],
    "teacher": ["student"],
    "student": []
}

def can_create_role(requester_role: str, target_role: str) -> bool:
    """Check if requester can create target role"""
    return target_role in role_hierarchy.get(requester_role, [])

# Dependency factory for role-based access
def require_role(required_roles: list[str]):
    def role_checker(current_user=Depends(get_current_user)):
        allowed_roles = []
        for role in required_roles:
            allowed_roles.append(role)
            allowed_roles.extend(role_hierarchy.get(role, []))
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        return current_user
    return role_checker

# Convenience shortcuts
require_superadmin = require_role(["superadmin"])
require_admin_or_above = require_role(["superadmin", "admin"])
require_teacher_or_above = require_role(["superadmin", "admin", "teacher"])
