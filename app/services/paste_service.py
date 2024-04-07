from app.exceptions import (
    PasteWasNotCreated, 
    PasteWasNotFound, 
    PasteWasNotRemoved, 
    PasteWasNotUpdated,
)
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.repositories.cloud_repository import CloudRepository
from app.models.paste_model import Paste
from app.schemas.paste_schemas import PasteCreateModel, PasteUpdateModel, PasteViewModel, PasteModel
from logger import logger
from app.core.cloud import bucket


class PasteService:
    def __init__ (self, db_repo: SqlAlchemyRepository, cloud_repo: CloudRepository):
        self.db_repo: SqlAlchemyRepository = db_repo(model=Paste)
        self.cloud_repo: CloudRepository = cloud_repo(bucket=bucket())

    async def create(
            self, 
            data: PasteCreateModel, 
            text: str,
            paste_id: str
    ) -> PasteViewModel:
        try:
            data = data.model_dump()
            paste_data = await self.db_repo.create(data)
            self.cloud_repo.create(key=paste_id, data=text)
            return PasteViewModel(**paste_data.__dict__, text=text)
            
        except Exception as e:
            logger.error(e)
            raise PasteWasNotCreated
        
    async def update(self, id, data: PasteUpdateModel, text: str):
        try:
            await self.db_repo.update(data, id=id)
            self.cloud_repo.update(id, text)
        except Exception as e:
            logger.error(e)
            raise PasteWasNotUpdated
        
    async def delete(self, id) -> None:
        try:
            await self.db_repo.delete(id=id)
            self.cloud_repo.delete(key=id)
        except Exception as e:
            logger.error(e) 
            raise PasteWasNotRemoved
            
    async def get_single(self, id) -> PasteModel:
        paste_data = await self.db_repo.get_single(id=id)
        paste_text = self.cloud_repo.get_single(id)

        if not(paste_data and paste_text):
            raise PasteWasNotFound
    
        return PasteModel(**paste_data.__dict__, text=paste_text['Body'].read().decode('utf-8'))

    async def get_all(self, **filters) -> list[PasteViewModel]:
        try:
            pastes = await self.db_repo.get_all(**filters)
            view_pastes = []
            for paste in pastes:
                view_pastes.append(PasteViewModel(**paste.__dict__, text=''))
            return view_pastes

        except Exception as e:
            logger.error(e)
            

            
