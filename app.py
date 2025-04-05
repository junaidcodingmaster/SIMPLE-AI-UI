from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    send_from_directory,
    redirect,
    make_response,
)
import requests
import threading
import queue
from ollamaClient import OllamaClient
from dotenv import load_dotenv
import os
import hashlib
from uuid import uuid4
from base64 import b64encode
from itsdangerous import URLSafeSerializer
import markdown

# ===================== INITIALIZATION =====================
# Initialize Flask app and Ollama client
app = Flask(__name__)
ai = OllamaClient()

# Queue for handling asynchronous chat requests
request_queue: queue.Queue = queue.Queue()
auth_portal_api_url = ""
no_of_auth_reqs = 0
no_of_reqs = 0

# Load environment variables from .env file
load_dotenv("./config.env")


# ===================== HELPER FUNCTIONS =====================
def get_config(key, default=None):
    """
    Retrieve a configuration value from environment variables.
    Exits the program if the key is not found and no default is provided.
    """
    value = os.getenv(key, default)
    if value is None:
        print(f"Error: The {key} is not set in the environment.")
        exit(1)  # Exit with non-zero status to indicate an error occurred
    return value


# ===================== CONFIGURATION =====================
# Load configuration from environment variables
config = {
    "host": get_config("SIMPLE_AI_UI_SERVER_HOST"),
    "port": int(get_config("SIMPLE_AI_UI_SERVER_PORT")),
    "users": {
        pair.split(":")[0]: pair.split(":")[1]
        for pair in get_config("SIMPLE_AI_UI_AUTH_USERS").split(",")
        if ":" in pair
    },
    "limit_of_auth_requests": int(get_config("SIMPLE_AI_UI_AUTH_NO_OF_USERS_PER_DAY")),
    "limit_of_requests": int(get_config("SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY")),
}


# ===================== AUTHENTICATION AND SECURITY =====================
def auth(username, password):
    """
    Authenticate a user by checking their username and password.
    Returns "OK-12" if authentication is successful, otherwise an error code.
    """
    if username in config["users"]:
        if hashing(config["users"][username]) == hashing(password):
            return "OK-12"
        else:
            return "BAD-2"
    return "BAD-12"


def hashing(text):
    """
    Hash a given text using SHA-256.
    """
    hash_object = hashlib.sha256(text.encode("utf-8"))
    return hash_object.hexdigest()


def middleware_check(type):
    """
    Middleware to check if the user is authenticated.
    Redirects to the login page or returns an error if not authenticated.
    """
    global no_of_auth_reqs
    try:
        auth_cookies = request.cookies.get("auth", "")
    except ValueError:
        auth_cookies = ""

    if auth_cookies == "":
        if type == "api":
            return jsonify(
                {
                    "error": "Auth error, You are not logged in!\n Login via <a href='/login'>LOGIN PAGE</a>"
                }
            )
        else:
            return redirect("/login")
    else:
        no_of_auth_reqs += 1
        return None


def middleware_init(username):
    """
    Initialize middleware by generating a token for the authenticated user.
    """
    global no_of_auth_reqs
    data = {
        "device": request.headers.get("User-Agent"),
        "user": username,
        "ID": str(uuid4()),
        "number": no_of_auth_reqs,
    }
    token, _ = server_encode_tokenizer(data)
    return token


def server_encode_tokenizer(data):
    """
    Encode data into a token using a URL-safe serializer.
    """
    key = str(uuid4())
    with open(".keys", "a") as f:
        f.write(key + "\n")
    auth_s = URLSafeSerializer(
        key + "-abujuni.dev", "Hi I am Junaid, Support my project"
    )
    token = auth_s.dumps(data)
    return token, auth_s


def server_decode_tokenizer(token, auth_s):
    """
    Decode a token back into data using a URL-safe serializer.
    """
    data = auth_s.loads(token)
    return data


# ===================== BACKGROUND WORKER THREAD =====================
def process_requests() -> None:
    """
    Worker thread function to process queued chat requests.
    """
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


# ===================== ROUTES =====================
# ============= FRONTEND ROUTES =============
@app.route("/")
def index():
    """
    Render the index page after checking authentication.
    """
    middleware_response = middleware_check(type="html")
    if middleware_response:
        return middleware_response
    return render_template("index.html"), 200


@app.route("/static/<path:filename>")
def serve_static(filename: str):
    """
    Serve static files from the 'static' directory.
    """
    return send_from_directory("static", filename), 200


@app.errorhandler(Exception)
def handle_error(error: Exception):
    """
    Handle errors and render appropriate error pages.
    """
    if hasattr(error, "code") and error.code == 404:
        return render_template("404.html"), 404
    return render_template("error.html", error=str(error)), 500


# ============= SECURITY ROUTES =============
@app.route("/login", methods=["GET", "POST"])
def api_auth():
    """
    Handle user login. Authenticates the user and sets an auth cookie if successful.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        auth_result = auth(username, password)
        if auth_result == "OK-12":
            token = middleware_init(username)
            response = make_response(redirect("/"))
            response.set_cookie("auth", token)
            return response
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


# ============= API ROUTES =============
@app.route("/api/connection")
def api_connection():
    """
    Check the connection to the Ollama server.
    """
    middleware_response = middleware_check(type="api")
    if middleware_response:
        return middleware_response
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
    """
    Retrieve statistics about available and active models from the Ollama client.
    """
    middleware_response = middleware_check(type="api")
    if middleware_response:
        return middleware_response
    models = ai.list_models()
    active_models = ai.list_active_models()

    if not models and not active_models:
        return jsonify({"error": "No models found"}), 404

    return jsonify({"available": models, "active": active_models}), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Handle chat requests by processing the prompt and model, and returning the AI's response.
    """
    middleware_response = middleware_check(type="api")
    if middleware_response:
        return middleware_response

    data = request.json
    if not data or "prompt" not in data or "model" not in data:
        return jsonify({"error": "Invalid request data"}), 400

    response_queue = queue.Queue()
    request_queue.put((data, response_queue))

    response = response_queue.get()

    if "response" not in response:
        return jsonify({"error": "Invalid response from the AI"}), 500

    html_response = markdown.markdown(response["response"])

    return jsonify({"response": html_response}), 200


# ===================== MAIN EXECUTION =====================
if __name__ == "__main__":
    app.run(host=config.get("host"), port=config.get("port"))