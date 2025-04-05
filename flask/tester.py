import jwt
from datetime import datetime
payload = {
    "sid": "test_session_id",
    "aud": "flask-app",
    "exp": 1735687200
}

secret = "your-secret"
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)

exp =1741541546
if exp and datetime.utcnow() > datetime.utcfromtimestamp(exp):
    print("123")