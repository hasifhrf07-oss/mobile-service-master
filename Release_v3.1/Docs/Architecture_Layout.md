# Mobile Service Master v3.1 - Structural Architecture

## File-by-File Read System
1. **web_app.py** (Core Flask App)
   - Routes incoming requests (Admin/Client).
   - Connects to SQLite via `database/db_path.py`.
   - Handles API endpoints for ADB, Scanners, and AI Engine.
2. **database/** (SQLite Storage)
   - `db_path.py`: Resolves path (`/var/data` on Render, `local_data/` on Windows).
   - `models.db`: 12,079 mobile models, 172 brands.
3. **b2b_core/** (Compliance & Limits)
   - `compliance.py`: Verifies legal docs before execution.
   - `limits.py`: Controls test-mode dynamic limits.
4. **android_tools/** (Telemetry)
   - `telemetry.py`: Handles ADB/MTK sandbox testing.
5. **Executables/** (Desktop Apps)
   - `Admin_App.exe`: Opens Admin Dashboard & starts server.
   - `Client_App.exe`: Opens Client Dashboard & starts server.

## Architectural Working System Layout
- **Local Mode:** User -> Client.exe -> localhost:5000 -> Flask -> SQLite.
- **Cloud Mode:** User -> https://mobile-service-master.onrender.com -> Gunicorn -> Flask -> Persistent Disk.
- **Admin Flow:** Admin.exe -> localhost:5000 (Admin) -> Approves Tools/Requests -> Auto-run engines (ADB/Scanners).
