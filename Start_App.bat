@echo off
title Mobile Service Master Server
color 0A
echo ===================================================
echo     MOBILE SERVICE MASTER - DAILY LOCAL SERVER
echo ===================================================
echo.

:: Set Environment Variables
set RENDER=true
set DEV_MODE=true

:: Get Local IP Address
echo Fetching Network IP...
for /f "delims=" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch 'Loopback' -and $_.PrefixOrigin -eq 'Dhcp'}).IPAddress | Select-Object -First 1"') do set LOCAL_IP=%%a

echo.
echo [ YOUR PC ]      http://127.0.0.1:5000
if not "%LOCAL_IP%"=="" (
    echo [ SHARE WITH OTHERS ] http://%LOCAL_IP%:5000
) else (
    echo [ SHARE WITH OTHERS ] Network IP Not Found
)
echo.
echo ===================================================
echo Starting Server... (Keep this window open)
echo Press Ctrl+C or Close this window to STOP.
echo ===================================================
echo.

:: Wait 2 seconds and open browser
start "" cmd /c "timeout /t 2 >nul && start http://127.0.0.1:5000"

:: Run the server (this keeps the window open and running)
python web_app.py

:: If server stops, pause so user can see errors
echo.
echo Server stopped. Press any key to exit.
pause >nul
