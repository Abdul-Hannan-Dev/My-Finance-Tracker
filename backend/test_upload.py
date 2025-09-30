import requests

UPLOAD_URL = "http://127.0.0.1:5000/upload"
REGISTER_URL = "http://127.0.0.1:5000/register"
LOGIN_URL = "http://127.0.0.1:5000/login"

resp = requests.post(REGISTER_URL, json={"username": "user4", "password": "pas125"})
print("Register:", resp.json())
user_id = resp.json().get("user_id")

files = {"file": open("dummy_transactions.csv", "rb")}
data = {"user_id": user_id}

resp = requests.post(UPLOAD_URL, files=files, data=data)
print("Upload:", resp.json())

GET_TXNS_URL = f"http://127.0.0.1:5000/transactions?user_id={user_id}"
resp = requests.get(GET_TXNS_URL)
print("Transactions:", resp.json())
