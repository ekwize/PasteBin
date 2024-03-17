import pytest
from app.core.database import get_session
from app.services.sqlalchemy_repository import SqlAlchemyRepository
from app.models.paste_model import Paste
from app.models.user_model import User
from app.schemas.user_schemas import UserCreateModel


# @pytest.mark.parametrize()
# async def test_create_user_func():
#     user_repo = SqlAlchemyRepository(User, get_session())
        




# @pytest.mark.parametrize()
# async def test_create_user_func():
#     ...