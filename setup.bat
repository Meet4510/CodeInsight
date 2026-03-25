@echo off
REM CodeInsight - Windows Setup Script
REM This script helps with initial setup on Windows

echo.
echo ========================================
echo CodeInsight - Windows Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo OK: Python is installed
echo.

REM Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install requirements
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo OK: Dependencies installed
echo.

REM Check MySQL
echo Checking MySQL...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MySQL is not installed or not in PATH
    echo Please install MySQL from https://dev.mysql.com/downloads/mysql/
    echo.
) else (
    echo OK: MySQL is installed
    echo.
)

REM Reminder
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create database:
echo    mysql -u root -p -e "source %%CD%%\database.sql"
echo    OR use MySQL Workbench/phpMyAdmin to import database.sql
echo.
echo 2. Update database credentials in app.py (if needed)
echo.
echo 3. Run application:
echo    python app.py
echo.
echo 4. Open browser and go to:
echo    http://localhost:5000
echo.
echo ========================================
echo.

pause
