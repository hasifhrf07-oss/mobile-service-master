@echo off
cd /d "%~dp0"
title Mobile Service Master - Local Server
echo Starting Local Server in background...
start "" /B pythonw web_app.py
timeout /t 3 /nobreak > NUL
echo Opening Dashboards...
start http://127.0.0.1:5000/?role=admin
start http://127.0.0.1:5000/?role=client
echo System is ready. You can close this window.
timeout /t 3 > NUL
exit
