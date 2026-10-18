# Mobile Service Master v3.1 - Architecture Blueprint
## 1. System Architecture
- **Web Core:** Flask (Python 3.11.9) serving both Admin and Client dashboards.
- **Desktop UI:** PyQt6 (Executables) acting as a web-wrapper/launcher for the local/cloud server.
- **Database:** SQLite3 (12,079 mobile models, 172 brands).
- **Automation Engines:** ADB, MTK/Qualcomm Fastboot, Camera/Board Scanners.

## 2. Working Flow Design
1. **User Client:** Opens `Client.exe` -> Connects to Localhost (Port 5000) -> Selects device -> Requests Unlock/Service.
2. **Admin System:** Opens `Admin.exe` -> Connects to Localhost -> Manages requests -> Uses ADB/Fastboot tools.
3. **AI & Automation:** Auto-answer engine processes client queries before Admin intervention.

## 3. Local & International Setup
- **Local:** `http://127.0.0.1:5000` (LAN enabled for team).
- **International:** `https://mobile-service-master.onrender.com` (Cloud deployed).
