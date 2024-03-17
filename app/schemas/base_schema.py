from typing import NewType

from pydantic import BaseModel, ConfigDict
from app.models.paste_model import Paste
from app.models.user_model import User

class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


