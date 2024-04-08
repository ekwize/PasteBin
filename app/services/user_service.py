from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.models.user_model import User
from app.schemas.user_scheme import UserCreateModel, UserUpdateModel


class UserService:
    def __init__ (self, repo: SqlAlchemyRepository):
        self.user_repo: SqlAlchemyRepository = repo(model=User)

    async def create(self, user_data: UserCreateModel):
        user_data = user_data.model_dump()
        await self.user_repo.create(user_data)

    async def update(self, data: UserUpdateModel, **filters) -> UserUpdateModel:
        data = data.model_dump()
        user = await self.user_repo.update(data, **filters)
        return user
        
    async def get_single(self, **filters) -> User:
        return await self.user_repo.get_single(**filters)