from fastapi import FastAPI

from src.api.reminders import router as reminders_router
from src.api.users import router as users_router

app = FastAPI(title="TG Assistant API")

app.include_router(users_router)
app.include_router(reminders_router)
