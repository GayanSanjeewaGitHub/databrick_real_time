@echo off
REM Setup script for Windows

echo =====================================
echo Data Pipeline Setup (Windows)
echo =====================================

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo ✓ Created .env file
)

REM Create Python virtual environment
echo.
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✓ Virtual environment created

REM Install dependencies
echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✓ Dependencies installed

REM Create data directories
echo.
echo Creating data directories...
if not exist data\raw\transactions mkdir data\raw\transactions
if not exist data\raw\weblogs mkdir data\raw\weblogs
if not exist data\processed mkdir data\processed
if not exist data\swamp mkdir data\swamp

echo ✓ Directories created

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Next steps:
echo 1. Review and update .env file if needed
echo 2. Start services: docker-compose up -d
echo 3. Wait for services to be ready (~2 minutes)
echo 4. Run: python src\data_generator.py
echo 5. Run: python src\pipeline_no_hms.py  (Data Swamp demo)
echo 6. Run: python src\pipeline_with_hms.py (Governed approach)
echo 7. Run: python src\propensity_model.py (Full pipeline)
echo.
pause
