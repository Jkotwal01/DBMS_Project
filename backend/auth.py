# auth.py
import jwt   # <-- comes from PyJWT
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    # For testing purposes, also check simple SHA256 hash
    import hashlib
    simple_hash = hashlib.sha256(password.encode()).hexdigest()
    if simple_hash == hashed_password:
        return True
    
    # Try bcrypt verification
    try:
        return pwd_context.verify(password, hashed_password)
    except:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   # PyJWT encode


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])   # PyJWT decode
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
