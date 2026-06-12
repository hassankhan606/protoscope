@echo off
echo ================================================
echo   BioDiscover - Quick Setup (Windows)
echo ================================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
echo Done.

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [4/4] All done! Run the app with:
echo   python src/main.py
echo.
pause
