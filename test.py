import requests

url = "http://127.0.0.1:5000/api/chat"
data = {"prompt": "HI", "model": "llama3.2:latest"}

try:
    res = requests.post(url,data=data)
    print(f"[LOG] Status Code : {res.status_code}")
    print(f"[LOG] Response : {res.content}")
except Exception as e:
    print(f"[ERROR] Response : {e}")



