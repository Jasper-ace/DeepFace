@echo off
echo Face Recognition Authentication System - Network Mode
echo ====================================================
echo.

REM Get the current IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "IP=%%b"
        goto :found
    )
)

:found
REM Remove leading spaces
for /f "tokens=* delims= " %%a in ("%IP%") do set IP=%%a

echo Detected IP Address: %IP%
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
echo Network Access: http://%IP%:8000
echo Local Access: http://localhost:8000
echo.
echo Other devices on your network can access: http://%IP%:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver %IP%:8000

pause