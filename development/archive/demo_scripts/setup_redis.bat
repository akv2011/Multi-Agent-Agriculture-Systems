@echo off
echo Setting up Redis for Multi-Agent Agriculture Systems...
echo.

REM Check if Redis is already running
echo Checking if Redis is already running...
netstat -an | find ":6379" >nul
if %errorlevel%==0 (
    echo Redis is already running on port 6379!
    goto :test_redis
)

echo Redis is not running. Let's set it up...
echo.

REM Option 1: Try to download portable Redis
echo Downloading portable Redis for Windows...
curl -L -o redis-windows.zip "https://github.com/redis-windows/redis-windows/releases/download/7.2.4/Redis-7.2.4-Windows-x64.zip"

if exist redis-windows.zip (
    echo Extracting Redis...
    powershell -command "Expand-Archive -Path redis-windows.zip -DestinationPath redis-windows -Force"
    
    if exist redis-windows\redis-server.exe (
        echo Starting Redis server...
        start "Redis Server" /min redis-windows\redis-server.exe redis-windows\redis.conf
        timeout /t 3 >nul
        goto :test_redis
    )
)

echo.
echo Could not set up portable Redis automatically.
echo.
echo Please choose one of these options:
echo.
echo 1. Install WSL2 (requires reboot):
echo    - Run: wsl --install
echo    - Reboot your computer
echo    - Then run the WSL setup commands
echo.
echo 2. Install Docker Desktop and run:
echo    - docker run -d -p 6379:6379 redis:alpine
echo.
echo 3. Use the existing mock Redis (current fallback)
echo    - Your application will work but without Redis persistence
echo.

:test_redis
echo Testing Redis connection...
python -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('✅ Redis is working!')
    print('Connection successful on localhost:6379')
except:
    print('❌ Could not connect to Redis')
    print('Using mock Redis for development')
"

echo.
echo Setup complete! Your agriculture system can now run.
pause
