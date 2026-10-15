from settings import PAID_TOOLS, get_api_key, is_tool_enabled
import requests

class APIManager:
    def __init__(self):
        self.tools = PAID_TOOLS

    def execute_tool(self, tool_name, operation, data):
        if not is_tool_enabled(tool_name):
            return {"status": "error", "message": f"{tool_name} er API key add kora hoyni."}
        api_key = get_api_key(tool_name)
        api_url = self.tools[tool_name]["api_url"]
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{api_url}{operation}", json=data, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"API call failed: {str(e)}"}

    def list_tools(self):
        return self.tools

    def add_tool_key(self, tool_name, api_key):
        if tool_name in self.tools:
            self.tools[tool_name]["api_key"] = api_key
            self.tools[tool_name]["enabled"] = True
            return {"status": "success", "message": f"{tool_name} API key added!"}
        return {"status": "error", "message": "Tool paoa jayni"}
