@echo off
REM Run Robot Framework tests with web server
echo ========================================
echo LDP Test Automation - Run Tests with Server
echo ========================================
echo.

REM Get the project directories - support LDP Project under Automation_Project or at Krungsri Tasks level
set "TEST_DIR=%~dp0"
set "LDP_PROJECT=%~dp0..\LDP Project"
if not exist "%LDP_PROJECT%" set "LDP_PROJECT=%~dp0..\..\LDP Project"

REM Check if server directory exists
if not exist "%LDP_PROJECT%" (
    echo ERROR: LDP Project directory not found. Tried:
    echo   - %~dp0..\LDP Project  (Automation_Project\LDP Project)
    echo   - %~dp0..\..\LDP Project  (Krungsri Tasks\LDP Project)
    pause
    exit /b 1
)
echo Using LDP Project at: %LDP_PROJECT%

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask is not installed. Installing dependencies...
    cd /d "%LDP_PROJECT%"
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Get port from argument or use default; optional 2nd arg = test path (e.g. tests\test_suites\03_select_card\test_select_card.robot)
set PORT=5000
set "TEST_PATH=tests/"
if not "%~1"=="" set PORT=%~1
if not "%~2"=="" set "TEST_PATH=%~2"

echo Starting web server on port %PORT%...
echo.

REM Start server in background
cd /d "%LDP_PROJECT%"
start "LDP Web Server" /MIN python server.py %PORT%

REM Wait for server to start
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

REM Check if server is running
curl -s http://localhost:%PORT%/authentication.html >nul 2>&1
if errorlevel 1 (
    echo WARNING: Server may not be ready yet. Continuing anyway...
)

echo.
echo ========================================
echo Running Robot Framework tests...
echo ========================================
echo.

REM Run tests
cd /d "%TEST_DIR%"
robot -d results %TEST_PATH%

set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
echo Tests completed with exit code: %TEST_EXIT_CODE%
echo ========================================
echo.

REM Stop the server (optional - comment out if you want to keep it running)
echo Stopping web server...
taskkill /FI "WINDOWTITLE eq LDP Web Server*" /T /F >nul 2>&1

if %TEST_EXIT_CODE% EQU 0 (
    echo All tests passed!
) else (
    echo Some tests failed. Check results/log.html for details.
)

pause
exit /b %TEST_EXIT_CODE%
