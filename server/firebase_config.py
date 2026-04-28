import firebase_admin
from firebase_admin import credentials, auth
import os
import json

# Path to service account JSON
# The user should provide this file
SERVICE_ACCOUNT_PATH = "firebase_service_account.json"

_firebase_app = None

def init_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return
        
    if os.path.exists(SERVICE_ACCOUNT_PATH):
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized.")
    else:
        print("WARNING: firebase_service_account.json not found. Firebase features will fail.")

def verify_id_token(id_token: str):
    try:
        init_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Firebase verification failed: {e}")
        return None
