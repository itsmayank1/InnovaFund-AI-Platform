"""
Week 3 preview: RBAC dependencies.
Included now so you can see how the role-permission matrix will plug in
later — you don't need to build this yet, just know it's coming.

Usage on a route later:
    @router.get("/admin-only")
    def admin_route(user=Depends(require_role(UserRole.ADMINISTRATOR))):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import decode_token
from app.models import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload  # contains sub (user id) and role


def require_role(*allowed_roles: UserRole):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return user
    return checker
