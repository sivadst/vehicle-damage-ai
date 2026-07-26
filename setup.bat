@echo off
echo ========================================
echo  Vehicle Damage AI - Windows Setup
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment
echo [1/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Install dependencies
echo [2/5] Installing dependencies...
pip install -r requirements.txt --quiet

:: Generate logo
echo [3/5] Generating application assets...
python -c "from app.utils.logo_generator import generate_logo; generate_logo()" 2>nul

:: Generate synthetic dataset
echo [4/5] Checking synthetic dataset...
if not exist "data\synthetic\dent" (
    echo Generating synthetic dataset...
    python src/data_pipeline.py
) else (
    echo Synthetic dataset already found.
)

:: Generate mock weights
echo [5/5] Generating initial model weights...
python -m src.train --demo-mode

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Run the following command to start:
echo   venv\Scripts\activate.bat
echo   streamlit run app/main.py
echo.
pause
