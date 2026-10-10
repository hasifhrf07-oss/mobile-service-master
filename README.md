# Mobile Service Master v3.0

Professional mobile repair intelligence system.

## Features

- 5-mode device detection (ADB/Fastboot/EDL/MTK/iPhone)
- Meter photo analysis (Analogue/Multimeter/DC Supply)
- Clone detection (7-rule scoring)
- Board scanner (state capture + compare)
- Technician dashboard + Admin analytics
- Self-learning comment engine
- 30-day privacy auto-cleanup
- 6-month free trial + subscription

## Local Run

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python web_app.py

Open: http://127.0.0.1:5000

## Deploy (Render)

1. Push to GitHub
2. Render -> New Web Service -> select repo
3. Auto-detects render.yaml
4. Done

## Live URL

https://mobile-service-master.onrender.com

## License

Private - All rights reserved
