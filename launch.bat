@echo off
REM Lead Machine launcher script
REM This script activates the virtual environment and runs the Streamlit app

cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run Streamlit
streamlit run app.py

pause
