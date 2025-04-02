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
        return jsonify({}), 404


# API endpoint to get connection stats (available and active models)
@app.route("/api/connection/stats")
def api_connection_stats():
    list_of_models = ai.listModels()
    list_of_active_models = ai.listActiveModels()

    # Handle cases where no models are available or active
    if not list_of_models and not list_of_active_models:
        return jsonify({}), 404

    # Prepare response data
    data = {
        "available": list_of_models,
        "active": list_of_active_models,
    }

    return jsonify(data), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()

    res = ai.chat(prompt=data.get("prompt"), model=data.get("model"))


# Main entry point
if __name__ == "__main__":
    app.run(debug=True)  # Set debug=True for development
