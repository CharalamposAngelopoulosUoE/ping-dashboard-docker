@echo off
cd /d "%~dp0.."

echo ========================================
echo Rebuild Database from CSV
echo ========================================

REM Prompt to delete old DB
set DB_PATH=logger\ping_dashboard.db
if exist "%DB_PATH%" (
    echo Old database found: %DB_PATH%
    set /p confirm="Delete old database and start fresh? (Y/N): "
    if /I "%confirm%"=="Y" (
        del "%DB_PATH%"
        echo [OK] Old database deleted.
    ) else (
        echo [INFO] Keeping existing database.
    )
)

REM Run migration
echo Importing CSV data into database...
python logger\migrate_csv_to_db.py

REM Run comparison
echo Verifying database against CSV...
python logger\compare_logs.py

echo ========================================
echo Done. Press any key to exit.
pause
