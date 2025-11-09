import hmac, hashlib
import os
from dotenv import load_dotenv
load_dotenv()
secret = os.getenv('WEBHOOK_SECRET')
with open("payload.json", "rb") as f:
    body = f.read()

signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
print("sha256=" + signature)
