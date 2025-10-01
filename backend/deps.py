# deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, RoleEnum
from auth import decode_access_token
from schemas import TokenData
import typing

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---- RBAC Utilities ----
class PermissionError(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def assert_user_has_role(current_user: "User", allowed_roles: list[str]):
    if current_user.role.value not in allowed_roles:
        raise PermissionError(f"Operation allowed only for roles: {', '.join(allowed_roles)}")
    return True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from auth import decode_access_token
    from sqlalchemy.exc import NoResultFound
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        assert_user_has_role(current_user, [role])
        return current_user
    return role_checker


def require_any_role(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        assert_user_has_role(current_user, list(roles))
        return current_user
    return role_checker
