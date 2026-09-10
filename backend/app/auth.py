
"""
JWT strategy (Week 1 decision, implemented here):
 
- ACCESS token: short-lived (15 min). Sent with every request. If stolen,
  damage window is small.
- REFRESH token: long-lived (7 days). Used only to get a new access token.
  Stored (hashed reference) in the refresh_tokens table so it can be revoked.
- Both tokens carry: sub (user id), role, exp, type ("access"/"refresh").
  Putting `role` in the token means RBAC checks don't need a DB hit on every
  request — middleware can trust the token once it's verified.
- Passwords hashed with bcrypt via passlib — industry standard, includes salt
  automatically, tunable work factor.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
 
import bcrypt
from jose import jwt, JWTError
 
# --- Config (move to env vars / secrets manager in production) ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
 
 
# --- Password hashing ---
# Using the bcrypt library directly (instead of via passlib) because passlib's
# bcrypt backend has a known compatibility bug with bcrypt>=4.1 (it tries to
# read a removed __about__.__version__ attribute and mishandles the 72-byte
# password limit). Calling bcrypt directly avoids both issues.
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")[:72]  # bcrypt's hard limit
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")
 
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
 
 
# --- Token creation ---
def _create_token(subject: str, role: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
 
def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        user_id, role, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )
 
 
def create_refresh_token(user_id: str, role: str) -> str:
    return _create_token(
        user_id, role, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )
 
 
# --- Token verification ---
def decode_token(token: str) -> Optional[dict]:
    """Returns the decoded payload, or None if invalid/expired."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None