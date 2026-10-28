@echo off
title Mini-Alexa Voice Assistant
cd /d "%~dp0"

echo ===================================================
echo           Mini-Alexa Voice Assistant
echo ===================================================
echo.

:: 1. Check for .env file; create from template if missing
if not exist ".env" (
    if exist ".env.example" (
        echo [.env] file not found. Initializing from .env.example...
        copy ".env.example" ".env" >nul
        echo [INFO] Created .env file. You can edit it to insert your API keys.
        echo.
    )
)

:: 2. Check for Python virtual environment; create and install if missing
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not detected.
    echo [INFO] Creating 'venv' using system Python...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo Please ensure Python 3.10+ is installed and available in your PATH.
        pause
        exit /b 1
    )
    echo [INFO] Installing required packages from requirements.txt...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo.
)

:: 3. Activate the virtual environment
call venv\Scripts\activate.bat

:: 4. Direct argument handling (e.g. run.bat --cli or run.bat --gui)
if not "%~1"=="" (
    if /i "%~1"=="--cli" (
        python main.py
        goto finish
    ) else if /i "%~1"=="--gui" (
        python gui.py
        goto finish
    ) else (
        python main.py %*
        goto finish
    )
)

:: 5. Interactive Mode Selection Menu (defaults to GUI after 5 seconds)
echo Select Startup Mode:
echo   [1] Graphical Interface (GUI Mode) - Default
echo   [2] Terminal Console Mode
echo.
choice /c 12 /t 5 /d 1 /m "Select option (auto-starting GUI in 5 seconds): "

if errorlevel 2 goto launch_terminal
if errorlevel 1 goto launch_gui

:launch_gui
echo.
echo [INFO] Launching Mini-Alexa Desktop GUI...
python gui.py
goto finish

:launch_terminal
echo.
echo [INFO] Launching Mini-Alexa Terminal Console...
python main.py
goto finish

:finish
if errorlevel 1 (
    echo.
    echo [ERROR] Mini-Alexa terminated with an error.
    pause
)
