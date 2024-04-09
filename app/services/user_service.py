from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.models.user_model import User
from app.schemas.user_scheme import UserCreateModel


class UserService:
    def __init__ (self, repo: SqlAlchemyRepository):
        self.user_repo: SqlAlchemyRepository = repo(model=User)

    async def create(self, user_data: UserCreateModel):
        user_data = user_data.model_dump()
        await self.user_repo.create(user_data)
        
    async def get_single(self, **filters) -> User:
        return await self.user_repo.get_single(**filters)