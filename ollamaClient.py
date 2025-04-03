import requests
import json

# Constants
OLLAMA_SERVER = "http://localhost:11434"
API_ENDPOINTS = {
    "list-models": "/api/tags",
    "list-active-models": "/api/ps",
    "chat": "/api/chat",
}


# Helper functions
def fetch_data(url):
    """Fetch data from a given URL using a GET request."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
        return {}


def send_data(url, data):
    """Send data to a given URL using a POST request."""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text  # Return text instead of raw content
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
        return ""


# Ollama Client Class
class OllamaClient:
    @staticmethod
    def list_models():
        """Fetch and return a list of available models."""
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-models"])
        if not data:
            return []

        models = data.get("models", [])
        return [
            {"name": item.get("name", ""), "model": item.get("model", "")}
            for item in models
        ]

    @staticmethod
    def list_active_models():
        """Fetch and return a list of active models."""
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-active-models"])
        if not data:
            return []

        models = data.get("models", [])
        return [
            {"name": item.get("name", ""), "model": item.get("model", "")}
            for item in models
        ]

    @staticmethod
    def chat(model, prompt):
        """Send a chat prompt to a specified model and return the response."""
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        response_text = send_data(OLLAMA_SERVER + API_ENDPOINTS["chat"], data)
        if not response_text:
            return ""

        # Parse the response (assuming it's a stream of JSON objects)
        parsed_lines = []
        for line in response_text.split("\n"):
            if line.strip():
                try:
                    parsed_lines.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"[LOG] ERROR: Failed to parse JSON - {e}")

        # Extract the message contents
        response_messages = [
            item.get("message", {}).get("content", "")
            for item in parsed_lines
            if "message" in item
        ]

        response_str = "".join(response_messages)

        print(
            f"[LOG] INCOMING DATA:\nmodel: {model}\nprompt: {prompt}\nOUTGOING:\nResponse: {response_str}"
        )

        return response_str
