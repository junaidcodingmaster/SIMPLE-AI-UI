from dotenv import load_dotenv
import os
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
        for pair in get_config("SIMPLE_AI_UI_AUTH_USERS", "joe:1234,apple:1234").split(
            ","
        )
        if ":" in pair
    },
    "open_stats": get_config("SIMPLE_AI_UI_AUTH_SHOW_USER_STATS", "true").lower()
    == "true",
    "limit_of_requests": int(
        get_config("SIMPLE_AI_UI_API_LIMIT_OF_REQS_PER_DAY", "1000")
    ),
    "limit_of_devices": int(get_config("SIMPLE_AI_UI_API_NO_OF_DEVICES", "1000")),
}


def auth(username, password):
    for user in config.get("users").keys():
        if user == username:
            if config.get("users").get(user) == password:
                return "OK-12"
            else:
                return "BAD-2"
        else:
            return "BAD-12"
        
print(auth("joe","124"))

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
        return False
