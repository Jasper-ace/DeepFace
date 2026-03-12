@echo off
echo Face Recognition Authentication System
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Start server
echo.
echo Starting Django development server...
echo Visit: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

pause