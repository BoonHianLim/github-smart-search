@echo off
setlocal

REM Detect platform-specific venv path
IF EXIST "venv\Scripts\activate.bat" (
    CALL venv\Scripts\activate.bat
) ELSE (
    echo No virtual environment found. Using system Python.
)

REM Run Streamlit app
streamlit run main.py
