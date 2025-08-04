@echo off
REM === Absolute project root ===
set PROJECT_ROOT=C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2
set PYTHON_EXE=C:\Users\cangelop\AppData\Local\Programs\Python\Python313\python.exe
set SCRIPT=%PROJECT_ROOT%\logger\daily_scan_DB.py

REM === Log start in file ===
echo [ %date% %time% ] Daily DB scan started >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"

REM === Run Python script (direct output to terminal) ===
"%PYTHON_EXE%" "%SCRIPT%"

REM === Log completion in file ===
echo [ %date% %time% ] Daily DB scan completed >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"
echo. >> "%PROJECT_ROOT%\logger\logs\daily_scan.log"

REM === Keep terminal open ===
pause

