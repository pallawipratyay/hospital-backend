from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str):
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated, hashed_password)
