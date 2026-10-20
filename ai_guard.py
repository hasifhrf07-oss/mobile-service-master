import json
import os

class AIGuard:
    def __init__(self):
        self.auth_file = "ai_auth.json"
        self.master_key = "MSM-ADMIN-AI-2026"
        self._initialize_auth()

    def _initialize_auth(self):
        if not os.path.exists(self.auth_file):
            auth_data = {
                "authorized_ais": {
                    "lead_architect": {"status": "active", "permissions": ["read", "write", "execute"]},
                    "client_bot": {"status": "active", "permissions": ["read"]},
                    "unauthorized_system": {"status": "blocked", "permissions": []}
                },
                "master_key": self.master_key
            }
            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            print("[*] AI Authorization File Created: ai_auth.json")

    def verify_ai(self, ai_name, api_key):
        with open(self.auth_file, 'r') as f:
            data = json.load(f)
        
        if api_key != data["master_key"]:
            return {"status": "error", "message": "Invalid Master Key"}
            
        if ai_name in data["authorized_ais"]:
            return data["authorized_ais"][ai_name]
        return {"status": "blocked", "message": "AI not registered"}

# টেস্ট রান
if __name__ == "__main__":
    guard = AIGuard()
    print(guard.verify_ai("lead_architect", "MSM-ADMIN-AI-2026"))
