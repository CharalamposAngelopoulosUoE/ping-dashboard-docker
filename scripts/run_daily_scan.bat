@echo off
REM --- Set project root explicitly ---
set PROJECT_ROOT=C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2

REM --- Go to project root ---
cd /d "%PROJECT_ROOT%"

REM --- Ensure log directory exists ---
if not exist "%PROJECT_ROOT%\logger\logs" mkdir "%PROJECT_ROOT%\logger\logs"

REM --- Full Python path ---
set PYTHON_EXE=C:\Users\cangelop\AppData\Local\Programs\Python\Python313\python.exe

REM --- Log start ---
echo [ %date% %time% ] Starting daily scan... >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"

REM --- Run Python and log output + show live (correct escaping) ---
powershell -Command "& '%PYTHON_EXE%' '%PROJECT_ROOT%\monitor\monitor.py' scan 2>&1 | Tee-Object -FilePath '%PROJECT_ROOT%\logger\logs\daily_scan.log' -Append"

REM --- Log completion ---
echo [ %date% %time% ] Daily scan completed. >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"
echo. >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"

pause
