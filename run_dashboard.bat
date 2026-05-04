@echo off
title BAHDA Survey Dashboard
echo ==========================================
echo Starting BAHDA Data Extraction and Dashboard
echo ==========================================

cd /d "%~dp0"

echo.
echo [1/2] Fetching latest CSV data from KoboToolbox...
python data_pipeline\run_pipeline.py
if %ERRORLEVEL% neq 0 (
    echo Error running pipeline! Press any key to start Streamlit anyway or close this window.
    pause >nul
)

echo.
echo [2/2] Launching Dashboard in your browser...
streamlit run app\streamlit_app.py

pause
