# app/services/auth_service.py

import time
import requests
from flask import session as flask_session
import config



class AuthService:

    @staticmethod
    def login(email, password, device_fingerprint):
        wizard_url = config.Config.API_SIGNIN_WIZARD
        signin_url = config.Config.API_SIGNIN
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        """Logs in the user and stores tokens in the session."""
        try:
            with requests.Session() as session:
                # Use Signin Wizard to get UUID
                wizard_response = session.get(wizard_url)
                wizard_response.raise_for_status()
                uuid = wizard_response.json().get("uuid")
                payload = {"uuid": uuid, "email": email, "password": password, "device_fingerprint": device_fingerprint}
                # Perform the login to get access and referesh tokens
                signin_response = session.post(signin_url, headers=headers, json=payload)
                signin_response.raise_for_status()
                if signin_response.status_code == 200:
                    cookies = session.cookies.get_dict()
                    data = signin_response.json().get("data", {})

                    # Save tokens and expiry in session
                    flask_session["accessToken"] = data['accessToken']['token']
                    flask_session["refreshToken"] = data['refreshToken']['token']
                    flask_session['cookies'] = cookies
                    flask_session["tokenExpiry"] = time.time() + 1200  # 20 minutes expiry

                return True
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            return False

    @staticmethod
    def is_token_expired():
        """Checks if the access token is expired."""
        token_expiry = flask_session.get("tokenExpiry")
        return not token_expiry or time.time() >= token_expiry

    @staticmethod
    def refresh_access_token():
        """Uses the refresh token to get a new access token."""
        refresh_token = flask_session.get("refreshToken")
        if not refresh_token:
            return False
        refresh_url = "https://api.affinitytrades.com/api/v2/my/refresh"
        payload = {"refreshToken": refresh_token}
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        cookies = flask_session.get('cookies', {})
        try:
            with requests.Session() as session:
                session.cookies.update(cookies)
                refresh_response = session.post(refresh_url, headers=headers, json=payload)
                refresh_response.raise_for_status()

                if refresh_response.status_code == 200:
                    cookies = session.cookies.get_dict()
                    data = refresh_response.json()

                    # Update tokens and expiry
                    flask_session["accessToken"] = data['accessToken']['token']
                    flask_session["refreshToken"] = data['refreshToken']['token']
                    flask_session['cookies'] = cookies
                    flask_session["tokenExpiry"] = time.time() + 1200  # 20 minutes expiry

                return True
        except requests.exceptions.RequestException as e:
            print(f"Token refresh failed: {e}")
            return False

    @staticmethod
    def get_access_token():
        """Returns a valid access token, refreshing it if necessary."""
        if AuthService.is_token_expired():
            if not AuthService.refresh_access_token():
                return None  # Token refresh failed
        return flask_session.get("accessToken")


