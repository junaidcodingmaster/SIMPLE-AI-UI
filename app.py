from flask import Flask, render_template, jsonify, request
import requests
from ollamaClient import OllamaClient
import threading
import queue

# Initialize Flask app and Ollama client
app = Flask(__name__)
ai = OllamaClient()

# Queue for handling requests
request_queue = queue.Queue()


def process_requests():
    while True:
        task = request_queue.get()
        if task is None:
            break  # Exit thread when None is received

        request_data, response_queue = task
        prompt = request_data.get("prompt")
        model = request_data.get("model")

        if not prompt or not model:
            response_queue.put({"error": "Invalid request data"})
        else:
            response = ai.chat(prompt=prompt, model=model)
            response_queue.put({"response": response})


# Start the background worker thread
worker_thread = threading.Thread(target=process_requests, daemon=True)
worker_thread.start()


@app.route("/")
def index():
    return render_template("index.html"), 200


@app.errorhandler(Exception)
def error_page(error):
    if hasattr(error, "code") and error.code == 404:
        return render_template("404.html"), 404
    return render_template("error.html", error=str(error)), 500


@app.route("/api/connection")
def api_connection():
    try:
        res = requests.get("http://localhost:11434", timeout=5)
        status_code = res.status_code
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("[LOG] ERROR: UNABLE TO CONNECT TO SERVER")
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
    list_of_models = ai.list_models()
    list_of_active_models = ai.list_active_models()

    if not list_of_models and not list_of_active_models:
        return jsonify({"error": "No models found"}), 404

    return jsonify({"available": list_of_models, "active": list_of_active_models}), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    response_queue = queue.Queue()
    request_queue.put((data, response_queue))

    # Wait for the response from the queue
    response = response_queue.get()
    return jsonify(response), 200 if "response" in response else 400


if __name__ == "__main__":
    app.run(debug=True)
