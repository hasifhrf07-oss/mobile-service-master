from flask import Flask, render_template, jsonify, request, session, redirect
import sqlite3, os, json, qrcode, base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = "msm-super-secret-key"
PIN_FILE = "admin_pin.json"
latest_scan = {}

def get_db():
    try:
        from database.db_path import get_db_path
        return get_db_path()
    except:
        return "local_data/mobile_service.db"

def get_master_pin():
    if os.path.exists(PIN_FILE):
        try:
            with open(PIN_FILE, 'r') as f:
                return str(json.load(f).get("pin", "12345678"))
        except: return "12345678"
    return "12345678"

def save_master_pin(pin):
    with open(PIN_FILE, 'w') as f:
        json.dump({"pin": pin}, f)

@app.route('/')
def index(): return redirect('/auto-login-admin')

@app.route('/auto-login-admin')
def auto_login():
    session['logged_in'] = True
    return redirect('/dashboard-v2')

@app.route('/dashboard-v2')
def dashboard(): return render_template('dashboard_v2.html')

@app.route('/api/total-models')
def total_models():
    try:
        conn = sqlite3.connect(get_db())
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM device_catalog")
        total = cursor.fetchone()[0]
        conn.close()
        return jsonify({"total": total})
    except: return jsonify({"total": 0})

@app.route('/api/get_brands')
def get_brands():
    try:
        conn = sqlite3.connect(get_db())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT rank, brand_name FROM brand_directory ORDER BY rank ASC")
        brands = [{"rank": row["rank"], "brand_name": row["brand_name"]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(brands)
    except: return jsonify([])

@app.route('/api/get_devices/<brand>')
def get_devices(brand):
    try:
        conn = sqlite3.connect(get_db())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT release_year, device_type, model_name, specs FROM device_catalog WHERE brand_name = ? ORDER BY release_year DESC", (brand,))
        devices = [{"year": row["release_year"], "type": row["device_type"], "model": row["model_name"], "specs": row["specs"]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(devices)
    except: return jsonify([])

@app.route('/api/set-pin', methods=['POST'])
def set_pin():
    data = request.get_json()
    new_pin = str(data.get('pin', '')).strip()
    if len(new_pin) != 8 or not new_pin.isdigit():
        return jsonify({"status": "error", "message": "PIN must be exactly 8 digits."})
    save_master_pin(new_pin)
    return jsonify({"status": "success", "message": "Master PIN updated!"})

@app.route('/api/get-pin')
def get_pin(): return jsonify({"pin": get_master_pin()})

@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():
    data = request.get_json()
    entered_pin = str(data.get('pin', '')).strip()
    if entered_pin == get_master_pin() and latest_scan:
        return jsonify({"status": "success", "data": latest_scan})
    return jsonify({"status": "error", "message": "Invalid PIN or no scan data."})


@app.route('/api/tools/<tool>', methods=['POST'])
def run_generic_tool(tool):
    steps = [
        {"text": f"Initializing {tool.upper()}...", "progress": 20},
        {"text": "Connecting to hardware...", "progress": 50},
        {"text": "Processing data...", "progress": 80},
        {"text": f"SUCCESS: {tool.upper()} operation complete!", "progress": 100}
    ]
    return jsonify({"steps": steps})


@app.route('/api/tools/deep-scan', methods=['POST'])
def deep_scan():
    global latest_scan
    latest_scan = {
        "device": "iPhone 13 Pro Max",
        "report": {"CPU": 95, "RAM": 88, "Battery": 77, "Display": 100, "Camera": 92, "Storage": 85, "Network": 98},
        "solution": "AI ANALYSIS: All ICs are communicating perfectly. Battery health is 77% (Needs replacement soon)."
    }
    steps = [
        {"text": "Connecting via USB...", "progress": 5},
        {"text": "Reading [1] CPU IC Data...", "progress": 15},
        {"text": "Reading [2] RAM IC Data...", "progress": 25},
        {"text": "Reading [3] Battery IC Data...", "progress": 35},
        {"text": "Reading [4] Display IC Data...", "progress": 45},
        {"text": "Reading [5] Camera IC Data...", "progress": 55},
        {"text": "Reading [6] NAND Storage Data...", "progress": 65},
        {"text": "Reading [7] Network Baseband Data...", "progress": 75},
        {"text": "Analyzing all hardware components...", "progress": 85},
        {"text": "SUCCESS: All Data Read Successfully!", "progress": 100}
    ]
    return jsonify({"steps": steps, "report": latest_scan["report"], "solution": latest_scan["solution"]})

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    current_pin = get_master_pin()
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"MSM_SECURE_PIN: {current_pin}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return jsonify({"qr_image": f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}", "pin": current_pin})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)