import config
import requests
from flask import session as flask_session
from app.services.service_account_manager import ServiceAccountManager

service_account_manager = ServiceAccountManager()
class Backend:

    @staticmethod
    def get_client_info(clientid):
        """Fetch client information"""
        try:
            response = service_account_manager.make_api_call("GET", "https://api.affinitytrades.com/api/v2/clients/9")
            if response.status_code == 200:
                print(response.json())


        except requests.exceptions.RequestException as e:
            print(f"Operation Failed: {e}")
            raise

    @staticmethod
    def get_account_info(account_id):
        try:
            url = f"https://api.affinitytrades.com/api/v2/accounts/{account_id}"
            response = service_account_manager.make_api_call("GET", url=url)
            if response.status_code == 200:
                return response.json()
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching profile data: {e}")
            return None