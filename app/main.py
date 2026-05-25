from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Travel Booking Assistant",
    version="1.0.0"
)

# Allow Streamlit (port 8501) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running"}