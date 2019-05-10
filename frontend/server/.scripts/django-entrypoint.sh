#!/bin/bash
cd /usr/src/app/
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python createUsers.py
python manage.py runserver 0.0.0.0:8000

