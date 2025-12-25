@echo off
REM Quick setup script for AI-Based Traffic Management System
REM Run this script to set up the environment and install dependencies


echo AI-Based Traffic Management System - Setup

echo.

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
echo.

echo [2/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.


echo Setup Complete!

echo To run the system:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run with webcam: python main.py
echo   3. Run with video: python main.py --input your_video.mp4
echo.
echo For more information, see README.md
