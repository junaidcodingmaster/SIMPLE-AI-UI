from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import threading
import queue
from ollamaClient import OllamaClient

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
    data = request.json
    response_queue: queue.Queue = queue.Queue()
    request_queue.put((data, response_queue))
    response = response_queue.get()  # Blocking wait for response
    status = 200 if "response" in response else 400
    return jsonify(response), status


if __name__ == "__main__":
    app.run()
