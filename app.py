from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import threading
import queue
from ollamaClient import OllamaClient
from dotenv import load_dotenv

import hashlib

# Load environment variables from .env file

load_dotenv("./config.env")


# Helper function to get configuration values

def get_config(key, default=None):

    value = os.getenv(key, default)

    if value is None:

        print(f"Error: The {key} is not set in the environment.")

        exit(1)  # Exit with non-zero status to indicate an error occurred

    return value


# Configuration

config = {

    "host": get_config("SIMPLE_AI_UI_SERVER_HOST", "0.0.0.0"),

    "port": int(get_config("SIMPLE_AI_UI_SERVER_PORT", "5000")),

    "users": {

        pair.split(":")[0]: pair.split(":")[1]

        for pair in get_config("SIMPLE_AI_UI_AUTH_USERS", "joe:1234,apple:1234").split(",")

        if ":" in pair

    },

    "open_stats": get_config("SIMPLE_AI_UI_AUTH_SHOW_USER_STATS", "true").lower() == "true",

    "limit_of_requests": int(get_config("SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY", "1000")),

    "limit_of_devices": int(get_config("SIMPLE_AI_UI_API_NO_OF_DEVICES", "1000")),

}
# Initialize Flask app and Ollama client
app = Flask(__name__)
ai = OllamaClient()

# Queue for handling asynchronous chat requests
request_queue: queue.Queue = queue.Queue()


def process_requests() -> None:
    """Worker thread function to process queued chat requests."""
    while True:
        task = request_queue.get()
        if task is None:
            break  # Exit when a termination signal is received

        request_data, response_queue = task
        prompt = request_data.get("prompt")
        model = request_data.get("model")

        if not prompt or not model:
            response_queue.put({"error": "Invalid request data"})
        else:
            response = ai.chat(model=model, prompt=prompt)
            response_queue.put({"response": response})


# Start background worker thread
threading.Thread(target=process_requests, daemon=True).start()

def auth(username, password):
    for user in config.get("users").keys():
        if user == username:
            if config.get("users").get(user) == password:
                return "OK-12"
            else:
                return "BAD-2"
        else:
            return "BAD-12"

def hashing(text):
    content = str(uuid4)+text+str(uuid4)
    hash_object = hashlib.sha256(content.encode("utf-8"))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def middlewares(username,password):
    auth_status=auth(username, password)
    if auth_status == "OK-12":
        hash_obj=hashing(username+password)
        request.cookies.add("auth":hash_obj)
        ALLOW_HASHS.append(hash_obj)
        return True
    else: 
        return render_template("error.html", error="YOU ARE NOT ALLOWED - AUTH ERROR")

def api_chat_func():
    data = request.json
    response_queue: queue.Queue = queue.Queue()
    request_queue.put((data, response_queue))
    response = response_queue.get()  # Blocking wait for response
    status = 200 if "response" in response else 400
    return jsonify(response), status

# Routes
@app.route("/")
def index():
    return render_template("index.html"), 200


@app.route("/static/<path:filename>")
def serve_static(filename: str):
    return send_from_directory("static", filename), 200


@app.errorhandler(Exception)
def handle_error(error: Exception):
    if hasattr(error, "code") and error.code == 404:
        return render_template("404.html"), 404
    return render_template("error.html", error=str(error)), 500


@app.route("/api/connection")
def api_connection():
    try:
        res = requests.get("http://localhost:11434", timeout=5)
        status_code = res.status_code
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        app.logger.error("Unable to connect to server")
        status_code = 404

    return (
        jsonify(
            {
                "host": "localhost",
                "port": 11434,
                "status": "OK" if status_code == 200 else "ERROR",
            }
        ),
        status_code,
    )


@app.route("/api/connection/stats")
def api_connection_stats():
    models = ai.list_models()
    active_models = ai.list_active_models()

    if not models and not active_models:
        return jsonify({"error": "No models found"}), 404

    return jsonify({"available": models, "active": active_models}), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    middlewares_firewall=middlewares()


if __name__ == "__main__":
    app.run()
