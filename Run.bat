@echo off
title INR18650-20R SOP Estimation Demo

cls
echo.
echo ============================================================
echo          INR18650-20R - STATE OF POWER (SOP) ESTIMATION
echo ============================================================
echo.

:: ============================
::  CHECK PYTHON
:: ============================
echo Checking Python installation...
python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is NOT installed or not added to PATH!
    echo Please install Python 3.9+ from python.org
    echo.
    pause
    exit /b 1
)

echo Python detected.
echo.

:: ============================
::  INSTALL REQUIRED PACKAGES
:: ============================
echo --------------------------------------------
echo Installing required Python libraries...
echo --------------------------------------------
echo.

pip install numpy pandas matplotlib openpyxl --quiet
pip install scipy

IF %ERRORLEVEL% NEQ 0 (
    color 4F
    echo [ERROR] Failed to install dependencies.
    echo Check your internet connection.
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.

:: ============================
::  RUN THE SOP ESTIMATION SCRIPT
:: ============================
echo --------------------------------------------
echo Running SOP Estimation Python Script...
echo --------------------------------------------
echo.

python sop_estimation_calce_inr18650_20r.py ^
  --xlsx "12_2_2015_Incremental OCV test_SP20-1.xlsx" ^
  --vmin 2.50 --vmax 4.20 ^
  --idismax 20 --ichgmax 4 ^
  --socmin 0.05 --socmax 0.95

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Script failed to run!
    echo Check the error message above.
    echo.
    pause
    exit /b 1
)

:: ============================
::  FINISH MESSAGE
:: ============================
echo.
echo ============================================================
echo ✅ SOP ESTIMATION COMPLETED SUCCESSFULLY!
echo Output files saved in the 'outputs' folder:
echo   - SOP_vs_Voltage.png
echo   - SOP_vs_Current.png
echo   - SOP_vs_SOC.png
echo ============================================================
echo.
pause
exit /b 0
