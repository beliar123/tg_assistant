#!/usr/bin/env sh
dockerize -wait 'tcp://postgres:5432'
alembic upgrade head
python main.py
