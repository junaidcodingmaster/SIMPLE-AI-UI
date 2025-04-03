import requests
import json

# Constants
OLLAMA_SERVER = "http://localhost:11434"
API_ENDPOINTS = {
    "list-models": "/api/tags",
    "list-active-models": "/api/ps",
    "chat": "/api/chat",
}


def fetch_data(url: str) -> dict:
    """Fetch data from a given URL using a GET request."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
    return {}


def send_data(url: str, data: dict) -> str:
    """Send data to a given URL using a POST request."""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        return response.text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
    return ""


def parse_models(data: dict) -> list:
    """Parse and return a list of models from response data."""
    models = data.get("models", [])
    return [
        {"name": item.get("name", ""), "model": item.get("model", "")}
        for item in models
    ]


class OllamaClient:
    @staticmethod
    def list_models() -> list:
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-models"])
        return parse_models(data)

    @staticmethod
    def list_active_models() -> list:
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-active-models"])
        return parse_models(data)

    @staticmethod
    def chat(model: str, prompt: str) -> str:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        response_text = send_data(OLLAMA_SERVER + API_ENDPOINTS["chat"], data)
        if not response_text:
            return ""

        response_lines = [line for line in response_text.splitlines() if line.strip()]
        response_messages = []
        for line in response_lines:
            try:
                json_line = json.loads(line)
                if "message" in json_line:
                    response_messages.append(
                        json_line.get("message", {}).get("content", "")
                    )
            except json.JSONDecodeError as e:
                print(f"[LOG] ERROR: Failed to parse JSON - {e}")

        response_str = "".join(response_messages)
        print(
            f"[LOG] INCOMING DATA:\nModel: {model}\nPrompt: {prompt}\nResponse: {response_str}"
        )
        return response_str
