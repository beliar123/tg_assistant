#!/usr/bin/env sh
alembic upgrade head
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
