#!/usr/bin/bash

sed -i 's/_bcrypt.__about__.__version__/_bcrypt.__version__/g' ./venv/lib/python3.13/site-packages/passlib/handlers/bcrypt.py
