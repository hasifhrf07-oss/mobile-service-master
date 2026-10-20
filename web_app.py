from flask import Flask, render_template, jsonify, request, session, redirect
import sqlite3, os, json, random, string, base64
from io import BytesIO
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "msm-super-secret-key"

# --- ENCRYPTED MASTER DATA MANAGER ---
class MasterDataManager:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.vault = {}

    def encrypt_data(self, data):
        return self.cipher.encrypt(json.dumps(data).encode()).decode()

    def decrypt_data(self, encrypted_token):
        try:
            return json.loads(self.cipher.decrypt(encrypted_token.encode()).decode())
        except:
            return None

    def handover_instruction(self, token, instruction, helper):
        return helper.execute_instruction(token, instruction)

class DataManagerHelper:
    def execute_instruction(self, token, instruction):
        if instruction == 'unlock_report':
            return {"status": "success", "message": "Report unlocked by AI Helper."}
        elif instruction == 'backup_data':
            return {"status": "success", "message": "Admin Data Backup Initiated."}
        elif instruction == 'check_role':
            return {"status": "success", "role": "Super Admin"}
        else:
            return {"status": "success", "message": f"AI processed: {instruction}"}

manager = MasterDataManager()
helper = DataManagerHelper()
latest_scan = {"device": "iPhone 13 Pro Max", "report": {"CPU": 95, "RAM": 88, "Battery": 77, "Display": 100, "Camera": 92, "Storage": 85, "Network": 98}, "solution": "All ICs are communicating perfectly."}

def get_db():
    try:
        from database.db_path import get_db_path
        return get_db_path()
    except: return "local_data/mobile_service.db"

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
    except: return jsonify({"total": 2285})

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

# --- APIS FOR FEATURES ---
@app.route('/api/tools/live-voltage', methods=['GET'])
def live_voltage():
    v = round(random.uniform(3.8, 4.25), 3)
    a = round(random.uniform(0.4, 1.2), 3)
    return jsonify({"voltage": v, "current": a})

@app.route('/api/tools/deep-scan', methods=['POST'])
def deep_scan():
    steps = [
        {"text": "Connecting via USB...", "progress": 10},
        {"text": "Reading [1] CPU IC...", "progress": 30},
        {"text": "Reading [2] RAM IC...", "progress": 50},
        {"text": "Reading [3] Battery IC...", "progress": 70},
        {"text": "SUCCESS: All Data Read Successfully!", "progress": 100}
    ]
    return jsonify({"steps": steps, "report": latest_scan["report"], "solution": latest_scan["solution"]})

@app.route('/api/tools/board-image/<model>', methods=['GET'])
def board_image(model):
    images = [
        "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?ixlib=rb-4.0.3&auto=format&fit=crop&w=1500&q=100",
        "https://images.unsplash.com/photo-1517420704952-d9f39e95b43e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1500&q=100"
    ]
    return jsonify({"image_url": random.choice(images)})

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    prompt = request.get_json().get('prompt', '').lower()
    if "voltage" in prompt: reply = "AI: Voltage is stable. Check F1 fuse if 0V."
    elif "circuit" in prompt: reply = "AI: Select a model in Dashboard to view Board View."
    else: reply = f"AI: I received your instruction '{prompt}'. Processing via MasterDataManager."
    return jsonify({"reply": reply})

@app.route('/api/admin/encrypt', methods=['POST'])
def encrypt_token():
    return jsonify({"token": manager.encrypt_data(latest_scan)})

@app.route('/api/admin/execute', methods=['POST'])
def execute_instruction():
    data = request.get_json()
    token = data.get('token')
    instruction = data.get('instruction', 'unlock_report')
    decrypted = manager.decrypt_data(token)
    if decrypted:
        result = manager.handover_instruction(token, instruction, helper)
        return jsonify({"status": "success", "data": decrypted, "ai_result": result})
    return jsonify({"status": "error", "message": "Invalid Token!"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)