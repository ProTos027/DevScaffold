#!/bin/bash

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver &
cd ..

# Frontend setup
cd frontend
npm install
npm start &
cd ..

echo "DevScaffold project started!"
