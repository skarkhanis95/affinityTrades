import time
import requests
from flask import session as flask_session
import config

config = config.Config()

API_BASE_URL = config.API_BASE_URL

def is_token_expired(token):
    token_expiry = flask_session.get("token_expiry")
    return time.time() >= token_expiry if token_expiry else True

def refresh_access_token():
    refresh_token = flask_session.get("refreshToken")
    if not refresh_token:
        return False
    response = requests.post(f"{API_BASE_URL}/auth/refresh", json={"refreshToken": refresh_token})
    if response.status_code == 200:
        data = response.json()
        flask_session["accessToken"] = data["accessToken"]
        flask_session["token_expiry"] = time.time() + 1800  # 30 mins
        return True
    return False

def get_access_token():
    if is_token_expired(flask_session.get("accessToken")):
        if not refresh_access_token():
            return None
    return flask_session.get("accessToken")
