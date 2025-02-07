import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session
from datetime import datetime
from app.models.wallets import Wallets
from app.services.service_account_manager import ServiceAccountManager

sm = ServiceAccountManager()
class Manager:
    @staticmethod
    def search_client(email):
        try:
            base_url = config.Config.search_clients
            url = f"{base_url}{email}"
            print(url)
            response = sm.make_api_call("GET", url=url)
            if response.status_code != 200:
                return None
            data = response.json()["data"]
            clients = []
            for client in data:
                clients.append(client)

            return clients

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Client Data: {e}")
            return None