#!/usr/bin/bash

rm -rf ./migrations/versions/* ./migrations/__pycache__
python3 ./drop_all_tables.py
alembic revision --autogenerate -m 'init all'
alembic upgrade head
