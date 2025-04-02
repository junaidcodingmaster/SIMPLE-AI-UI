from flask import Flask, send_from_directory, request, jsonify
import requests
from werkzeug.exceptions import NotFound
from ollamaClient import OllamaClient

# Constants
TEMPLATE_FOLDER = "./templates"

# Initialize Flask app and Ollama client
app = Flask(__name__)
ai = OllamaClient()


# Route to serve the main index page
@app.route("/")
def index():
    return send_from_directory(directory=TEMPLATE_FOLDER, path="index.html")


# Route to handle other static pages
@app.route("/<path:name>")
def page_handler(name):
    try:
        return send_from_directory(directory=TEMPLATE_FOLDER, path=name)
    except NotFound:
        return send_from_directory(directory=TEMPLATE_FOLDER, path="404.html"), 404


# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return send_from_directory(directory=TEMPLATE_FOLDER, path="404.html"), 404


# API endpoint to check connection to the Ollama server
@app.route("/api/connection")
def api_connection():
    try:
        # Attempt to connect to the Ollama server
        res = requests.get("http://localhost:11434", timeout=5)
        status_code = res.status_code
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("[LOG] ERROR: UNABLE TO CONNECT TO SERVER")
        status_code = 404

    # Return appropriate response based on connection status
    if status_code == 200:
        return jsonify({"host": "localhost", "port": 11434, "status": "OK"}), 200
    else:
        return jsonify({"error": "Unable to connect to server"}), 404


# API endpoint to get connection stats (available and active models)
@app.route("/api/connection/stats")
def api_connection_stats():
    list_of_models = ai.listModels()
    list_of_active_models = ai.listActiveModels()

    # Handle cases where no models are available or active
    if not list_of_models and not list_of_active_models:
        return jsonify({"error": "No models found"}), 404

    # Prepare response data
    data = {
        "available": list_of_models,
        "active": list_of_active_models,
    }

    return jsonify(data), 200


# API endpoint to handle chat requests
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()

    # Validate required fields in the request
    if not data or "prompt" not in data or "model" not in data:
        return jsonify({"error": "Missing 'prompt' or 'model' in request"}), 400

    try:
        # Send the chat request to the Ollama client
        res = ai.chat(prompt=data.get("prompt"), model=data.get("model"))
        return jsonify(res), 200
    except Exception as e:
        print(f"[LOG] ERROR: {e}")
        return jsonify({"error": "Failed to process chat request"}), 500

if __name__ == "__main__":
    app.run()  
