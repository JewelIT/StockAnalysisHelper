@echo off
REM Windows installer script for Stock Analysis Helper

echo.
echo ========================================
echo Stock Analysis Helper - Windows Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker is installed
    goto :docker_install
) else (
    echo [!] Docker not found
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
    goto :python_install
) else (
    echo [!] Python not found
)

echo.
echo Neither Docker nor Python found!
echo.
echo Please install one of the following:
echo   1. Docker Desktop: https://www.docker.com/products/docker-desktop
echo   2. Python 3.8+: https://www.python.org/downloads/
echo.
pause
exit /b 1

:docker_install
echo.
echo Installing via Docker...
echo.
docker-compose up -d
if %errorlevel% equ 0 (
    echo.
    echo [OK] Installation successful!
    echo.
    echo Opening browser...
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
) else (
    echo [!] Docker installation failed
    pause
)
exit /b 0

:python_install
echo.
echo Installing via Python...
echo.
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo.
    echo [OK] Installation successful!
    echo.
    echo Starting application...
    start /B python run.py
    timeout /t 5 /nobreak >nul
    start http://localhost:5000
) else (
    echo [!] Python installation failed
    pause
)
exit /b 0
