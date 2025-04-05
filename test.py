from itsdangerous import URLSafeSerializer
from uuid import uuid4

def server_encode_tokenizer(data):
    key=str(uuid4)
    with open("keys","a") as f:
        f.write(key+"\n")
    auth_s = URLSafeSerializer(key + "-abujuni.dev", "Hi I am Junaid, Support my project")
    token = auth_s.dumps(data)
    
    return(token,auth_s)

def server_decode_tokenizer(token,auth_s):
data = auth_s.loads(token)
print(data["name"])
