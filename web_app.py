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
        # Data Manager Helper executes the instruction
        return helper.execute_instruction(token, instruction)

class DataManagerHelper:
    def execute_instruction(self, token, instruction):
        # Simulated AI processing of instructions
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

# ডেমো ডেটা
latest_scan = {"device": "iPhone 13 Pro Max", "report": {"CPU": 95, "RAM": 88, "Battery": 77}, "solution": "AI Diagnosis..."}

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

# --- NEW ADVANCED APIS ---
@app.route('/api/tools/live-voltage', methods=['GET'])
def live_voltage():
    v = round(random.uniform(3.8, 4.25), 3)
    a = round(random.uniform(0.4, 1.2), 3)
    return jsonify({"voltage": v, "current": a, "status": "Stable" if v < 4.2 else "High Voltage!"})

@app.route('/api/tools/circuit-diagram/<brand>/<model>', methods=['GET'])
def circuit_diagram(brand, model):
    # মডেল অনুযায়ী ডায়াগ্রাম ডেটা
    return jsonify({
        "brand": brand, "model": model,
        "components": ["U2 Tristar IC", "PMIC 8020", "NAND Flash", "Wi-Fi IC"],
        "paths": ["VCC_MAIN -> U2", "VDD_CPU -> PMIC", "Antenna -> Wi-Fi IC"],
        "logic": "If VCC_MAIN is 0V, check F1 fuse and U2 IC."
    })

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    prompt = data.get('prompt', '').lower()
    
    if "voltage" in prompt:
        reply = "AI Assistant: Live voltage is currently stable. If you see 0V, check the F1 fuse."
    elif "backup" in prompt:
        reply = "AI Assistant: You can initiate the backup from the Admin Settings panel."
    elif "circuit" in prompt:
        reply = "AI Assistant: Please select a brand and model to view the master circuit diagram."
    else:
        reply = f"AI Assistant: I received your instruction '{prompt}'. The Master Data Manager has logged this."
        
    return jsonify({"reply": reply})

@app.route('/api/admin/encrypt-token', methods=['POST'])
def encrypt_token():
    data = request.get_json()
    encrypted = manager.encrypt_data(data.get('data', latest_scan))
    return jsonify({"token": encrypted})

@app.route('/api/admin/execute', methods=['POST'])
def execute_instruction():
    data = request.get_json()
    token = data.get('token')
    instruction = data.get('instruction', 'unlock_report')
    
    # ডিক্রিপ্ট এবং হেল্পার দিয়ে এক্সিকিউট
    decrypted = manager.decrypt_data(token)
    if decrypted:
        result = manager.handover_instruction(token, instruction, helper)
        return jsonify({"status": "success", "data": decrypted, "ai_result": result})
    return jsonify({"status": "error", "message": "Invalid Encrypted Token!"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)