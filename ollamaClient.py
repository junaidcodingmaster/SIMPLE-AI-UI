import requests
import json

# ===================== CONSTANTS =====================
# Base URL for the Ollama server
OLLAMA_SERVER = "http://localhost:11434"

# API endpoints for the Ollama server
API_ENDPOINTS = {
    "list-models": "/api/tags",  # Endpoint to list available models
    "list-active-models": "/api/ps",  # Endpoint to list active models
    "chat": "/api/chat",  # Endpoint for chat functionality
}


# ===================== HELPER FUNCTIONS =====================
def fetch_data(url: str) -> dict:
    """
    Fetch data from a given URL using a GET request.
    Returns the JSON response as a dictionary.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
    return {}  # Return an empty dictionary on error


def send_data(url: str, data: dict) -> str:
    """
    Send data to a given URL using a POST request.
    Returns the raw response text.
    """
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[LOG] ERROR: Unable to connect to server - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[LOG] ERROR: Request failed - {e}")
    return ""  # Return an empty string on error


def parse_models(data: dict) -> list:
    """
    Parse and return a list of models from the response data.
    Each model is represented as a dictionary with 'name' and 'model' keys.
    """
    models = data.get("models", [])
    return [
        {"name": item.get("name", ""), "model": item.get("model", "")}
        for item in models
    ]


# ===================== OLLAMA CLIENT CLASS =====================
class OllamaClient:
    """
    A client for interacting with the Ollama server.
    Provides methods to list models, list active models, and chat with a model.
    """

    @staticmethod
    def list_models() -> list:
        """
        Fetch and return a list of available models from the Ollama server.
        """
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-models"])
        return parse_models(data)

    @staticmethod
    def list_active_models() -> list:
        """
        Fetch and return a list of active models from the Ollama server.
        """
        data = fetch_data(OLLAMA_SERVER + API_ENDPOINTS["list-active-models"])
        return parse_models(data)

    @staticmethod
    def chat(model: str, prompt: str) -> str:
        """
        Send a chat request to the Ollama server and return the response.
        """
        # Prepare the data for the chat request
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Send the request and get the response
        response_text = send_data(OLLAMA_SERVER + API_ENDPOINTS["chat"], data)
        if not response_text:
            return ""  # Return an empty string if the response is invalid

        # Parse the response text (streamed JSON lines)
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

        # Combine all messages into a single response string
        response_str = "".join(response_messages)

        # Log the incoming data for debugging
        print(
            f"[LOG] INCOMING DATA:\nModel: {model}\nPrompt: {prompt}\nResponse: {response_str}"
        )

        return response_str
