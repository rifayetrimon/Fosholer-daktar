from fastapi import APIRouter
from app.modules.auth.controller import router as auth_router
from app.modules.chat.controller import router as chat_router
from app.modules.conversations.controller import router as conversations_router
from app.modules.crops.controller import router as crops_router
from app.modules.knowledge.controller import router as knowledge_router
from app.modules.scans.controller import router as scans_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(crops_router)
api_router.include_router(scans_router)
api_router.include_router(knowledge_router)
api_router.include_router(chat_router)
api_router.include_router(conversations_router)
