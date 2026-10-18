@echo off
echo Starting Mobile Service Master Local Server...
start /B python web_app.py
timeout /t 3 /nobreak > NUL
echo Opening Dashboards...
start http://127.0.0.1:5000/?role=admin
start http://127.0.0.1:5000/?role=client
echo System is ready. Keep this window open.
pause
