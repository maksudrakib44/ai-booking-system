import nest_asyncio
nest_asyncio.apply()          # ← must be at the very top

from fastapi import FastAPI
from app.routes.chat import router as chat_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Travel Booking Assistant",
    version="1.0.0"
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running"}