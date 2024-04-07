import base64
import secrets
from passlib.context import CryptContext
from app.models.paste_model import Paste

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_paste_id() -> str:
    id = secrets.token_bytes(6)
    hash = base64.urlsafe_b64encode(id)
    unique_id = hash.decode()
    return unique_id

def is_private(paste: Paste) -> bool:
    if paste.password:
        return True
    return False

def verify_paste_password(paste: Paste, password: str) -> bool:
    if is_private(paste):
        return pwd_context.verify(password, paste.password)
    return True
    