from flask import Flask, render_template, jsonify, request, session, redirect
import sqlite3, os, json, random

app = Flask(__name__)
app.secret_key = "msm-super-secret-key"

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

@app.route('/api/tools/<tool>', methods=['POST'])
def run_tool(tool):
    steps = [
        {"text": f"Initializing {tool.upper()}...", "progress": 20},
        {"text": "Connecting to hardware...", "progress": 50},
        {"text": "Processing data...", "progress": 80},
        {"text": f"SUCCESS: {tool.upper()} complete!", "progress": 100}
    ]
    return jsonify({"steps": steps})

@app.route('/api/live-voltages', methods=['GET'])
def live_voltages():
    return jsonify({
        "PMIC": round(random.uniform(4.1, 4.3), 2),
        "CPU": round(random.uniform(1.0, 1.2), 2),
        "NAND": round(random.uniform(1.7, 1.9), 2),
        "WiFi": round(random.uniform(3.2, 3.4), 2),
        "Display": round(random.uniform(5.3, 5.7), 2)
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
