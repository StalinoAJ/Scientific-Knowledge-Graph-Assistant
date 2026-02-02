@echo off
echo ===================================================
echo   Stopping Scientific Knowledge Graph Assistant
echo ===================================================
echo.

echo [1/1] Stopping and removing containers...
docker-compose down

if %errorlevel% neq 0 (
    echo.
    echo Error stopping application!
    pause
    exit /b
)

echo.
echo ===================================================
echo   Application stopped successfully.
echo ===================================================
echo.
pause
