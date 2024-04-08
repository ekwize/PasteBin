from fastapi import APIRouter
from .routes.paste import router as paste_router
from .routes.user import router as auth_router


routers = APIRouter()

routers.include_router(auth_router)
routers.include_router(paste_router)