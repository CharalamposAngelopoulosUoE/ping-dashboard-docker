@echo off
REM === Absolute project root ===
set PROJECT_ROOT=C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2
set PYTHON_EXE=C:\Users\cangelop\AppData\Local\Programs\Python\Python313\python.exe
set SCRIPT=%PROJECT_ROOT%\logger\weekly_report_v2.py
set LOG_FILE=%PROJECT_ROOT%\logger\logs\weekly_report.log

REM === Ensure log directory exists ===
if not exist "%PROJECT_ROOT%\logger\logs" mkdir "%PROJECT_ROOT%\logger\logs"

REM === Log start ===
echo [ %date% %time% ] Weekly report started >> "%LOG_FILE%"
echo [ %date% %time% ] Weekly report started

REM === Run Python script (direct output to terminal) ===
"%PYTHON_EXE%" "%SCRIPT%"

REM === Log completion ===
if %ERRORLEVEL% EQU 0 (
    echo [ %date% %time% ] Weekly report completed successfully >> "%LOG_FILE%"
) else (
    echo [ %date% %time% ] Weekly report failed (check above output) >> "%LOG_FILE%"
)
echo. >> "%LOG_FILE%"
echo [ %date% %time% ] Weekly report completed

REM === Keep terminal open ===
pause
