#!/usr/bin/bash

rm -rf ./migrations/versions/* ./migrations/__pycache__
python ./drop_all_tables.py
alembic revision --autogenerate -m 'create users table'
alembic upgrade head
