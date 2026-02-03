# Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
Start-Process python -ArgumentList "manage.py","runserver"
cd ..

# Frontend setup
cd frontend
npm install
Start-Process npm -ArgumentList "start"
cd ..

Write-Host "DevScaffold project started!"
