import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=============================================")
print(" MOBILE SERVICE MASTER - CLEAN & FAST CORE ")
print("=============================================")

try:
    from web_app import app
    print("[+] App loaded. Starting Server...")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
except Exception as e:
    import traceback
    traceback.print_exc()
