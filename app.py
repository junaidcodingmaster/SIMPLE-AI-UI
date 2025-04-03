from flask import Flask, render_template, jsonify, request
import requests
from ollamaClient import OllamaClient

# Initialize Flask app and Ollama client
app = Flask(__name__)
ai = OllamaClient()


# Route to serve the main index page
@app.route("/")
def index():
    return render_template("index.html"),200


@app.errorhandler(Exception)
def error_page(error):
    if hasattr(error, "code") and error.code == 404:
        return render_template("404.html"), 404

    return (
        render_template("error.html", error=str(error)),
        500,
    )  # Return 500 for general errors


# API endpoint to check connection to the Ollama server
@app.route("/api/connection")
def api_connection():
    try:
        res = requests.get("http://localhost:11434", timeout=5)
        status_code = res.status_code
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("[LOG] ERROR: UNABLE TO CONNECT TO SERVER")
        status_code = 404

    if status_code == 200:
        return jsonify({"host": "localhost", "port": 11434, "status": "OK"}), 200
    else:
        return jsonify({"error": "Unable to connect to server"}), 404


# API endpoint to get connection stats (available and active models)
@app.route("/api/connection/stats")
def api_connection_stats():
    list_of_models = ai.list_models()
    list_of_active_models = ai.list_active_models()

    if not list_of_models and not list_of_active_models:
        return jsonify({"error": "No models found"}), 404

    data = {
        "available": list_of_models,
        "active": list_of_active_models,
    }

    return jsonify(data), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    # Get JSON data from the request
    data = request.json
    prompt = data.get("prompt")
    model = data.get("model")

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    if not model:
        return jsonify({"error": "Missing 'model' in request"}), 400

    # Assuming ai.chat is a function that takes prompt and model as arguments
    res = ai.chat(prompt=prompt, model=model)

    # Return the response as JSON
    return jsonify({"response": res}), 200


if __name__ == "__main__":
    app.run(debug=True)  # Set debug=True for development
