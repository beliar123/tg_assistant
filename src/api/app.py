from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth_router import router as auth_router
from src.api.reminders import router as reminders_router
from src.api.users import router as users_router

app = FastAPI(title="TG Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reminders_router)
