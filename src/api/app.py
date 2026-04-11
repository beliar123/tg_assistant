from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.auth_router import router as auth_router
from src.api.limiter import limiter
from src.api.reminders import router as reminders_router
from src.api.users import router as users_router

app = FastAPI(title="TG Assistant API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reminders_router)
