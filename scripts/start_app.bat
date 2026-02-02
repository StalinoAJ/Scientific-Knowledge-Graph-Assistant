@echo off
echo ===================================================
echo   Scientific Knowledge Graph Assistant - Alpha
echo ===================================================
echo.

echo [1/3] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b
)
echo Docker is running.
echo.

echo [2/3] Building and Starting Application...
echo This may take a few minutes for the first run...
echo.
docker-compose down
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo Error starting application!
    pause
    exit /b
)

echo.
echo [3/3] Waiting for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo ===================================================
echo   SUCCESS! Application is running.
echo ===================================================
echo.
echo Access the App here: http://localhost:3000
echo API Docs available:  http://localhost:8000/docs
echo Neo4j Browser:       http://localhost:7474
echo.
echo NOTE: Ensure you have Ollama running with 'ollama serve'
echo.
pause
