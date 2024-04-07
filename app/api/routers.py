from fastapi import APIRouter
from .pastes import router as paste_router
from .users import router as auth_router


routers = APIRouter()

routers.include_router(auth_router)
routers.include_router(paste_router)