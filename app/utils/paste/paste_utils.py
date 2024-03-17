import base64
import secrets
from datetime import datetime, timedelta
import calendar
from app.utils.auth import verify_password


def create_paste_id() -> str:
    id = secrets.token_bytes(6)
    hash = base64.urlsafe_b64encode(id)
    unique_id = hash.decode()
    return unique_id

def is_private(paste) -> bool:
    if paste.password:
        return True
    return False

def verify_paste_password(paste, password) -> bool:
    if is_private(paste):
        return verify_password(password, paste.password)
    return True
    