import requests
import json

ollama_serve = "http://localhost:11434"
collection_of_apis = {
    "list-models": "/api/tags",
    "list-active-models": "/api/ps",
    "chat": "/api/chat",
}

def get_data(url):
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("[LOG] ERROR  : UNABLE TO CONNECT TO SERVER")
        data = {}

    return data

def post_data(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url, json=data, headers=headers,stream=True)
        content = res.text  # parse response as JSON
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("[LOG] ERROR : UNABLE TO CONNECT TO SERVER")
        content = {}

    return content

class OllamaClient:

    @staticmethod
    def listModels():
        data = get_data(ollama_serve + collection_of_apis.get("list-models"))

        if data == {}:
            return []

        filter_data = data.get('models')   # should be 'models' not 'model'

        results = []
        for item in filter_data:
            results.append({"name": item.get("name"), "model": item.get("model")})

        return results

    @staticmethod
    def listActiveModels():
        data = get_data(ollama_serve + collection_of_apis.get("list-active-models"))

        if data=={}:
            return []

        filter_data = data.get("models")  # should be 'models' not 'model'

        results = []
        for item in filter_data:
            results.append({"name": item.get("name"), "model": item.get("model")})

        return results

    @staticmethod
    def chat(model, prompt):
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        res = post_data(ollama_serve + collection_of_apis.get("chat"), data)
        # return res
        lines = res.split('\n')[:-1]
        parsed_json = []
        for line in lines:
            parsed_json.append(json.loads(line))

        results=[]
        for item in parsed_json:
            results.append(item["message"]["content"])

        return "".join(results)
