@echo off
cd /d "C:\mobile_service_master"
call venv\Scripts\activate.bat
title Mobile Service Master - ADMIN
color 4F
echo Starting Admin Server... Please wait.
start /B python web_app.py
timeout /t 4 /nobreak > NUL
start http://127.0.0.1:5000/dashboard-v2
exit
