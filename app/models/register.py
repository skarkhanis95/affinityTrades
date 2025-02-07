import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session
from datetime import datetime
from app.models.wallets import Wallets
import mysql.connector
from app.services.service_account_manager import ServiceAccountManager

sm = ServiceAccountManager()

db_config = {
    "host": config.Config.DB_HOST,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}
class Register:
    @staticmethod
    def create_pamm_account(accessToken, refreshToken, refId=None):

        try:
            print("Inside CREATE PAMM ACCOUNT")
            investor_pamm_account_id = None
            investor_pamm_account_number = None
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {accessToken}"
            }
            print(f"Headers for PAMM: {headers}")
            url = config.Config.CREATE_PAMM_ACCOUNT_URL
            print(f"BEFORE URL: {url}")
            response = requests.get(url=url, headers=headers)
            if response.status_code != 200:
                print(f"Response URL: {response.url}")
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                print(f"Response Content: {response.content}")
                return None
            data = response.json()["data"]
            account_uuid = data["uuid"]
            if not account_uuid:
                return None
            # Create Account With UUID
            wizard__url = f"https://api.affinitytrades.com/api/v1/wizards/{account_uuid}"
            pamm_account_payload = {
                "leverage": "100",
                "product_id": 28,
                "product_currency_id": 28,
                "groupType": 6
            }
            response = requests.post(url=wizard__url, headers=headers, json=pamm_account_payload)
            if response.status_code != 200:
                return None

            data = response.json()["data"]
            account_data = data.get("data", {}).get("account", {})
            investor_pamm_account_id = account_data.get("id")
            investor_pamm_account_number = account_data.get("account_id")

            if not investor_pamm_account_id or not investor_pamm_account_number:
                return None

            # accounts_url = config.Config.ACCOUNTS_API
            # response = requests.get(url=accounts_url, headers=headers)
            # if response.status_code != 200:
            #     return None
            # accounts = response.json()["data"]
            #
            # for account in accounts:
            #     if account.get("group", {}).get("id") == 16 and account.get("platform", {}).get("id") == 2:
            #         investor_pamm_account_id = account.get("accountId")
            #         investor_pamm_account_number = account.get("accountNumber")

            can_subscribe_url = config.Config.CAN_SUBSCRIBE_URL
            can_subscribe_payload = {
                "master_login": config.Config.MASTER_ACCOUNT_NUMBER,
                "investor_login": investor_pamm_account_number,
                "investment_platform_id": config.Config.INVESTMENT_PLATFORM_ID
            }
            response = requests.post(url=can_subscribe_url, headers=headers, json=can_subscribe_payload)
            if response.status_code != 200:
                return None
            can_subscribe_data = response.json()["data"]
            can_subscribe = can_subscribe_data.get("can_subscribe")
            if can_subscribe:
                subscribe_url = config.Config.SUBSCRIBE_URL
                subscribe_payload = {
                    "master_account_id": config.Config.MASTER_ACCOUNT_NUMBER,
                    "investor_account_id": investor_pamm_account_number,
                    "investment_platform_id": config.Config.INVESTMENT_PLATFORM_ID,
                    "allocation_method": config.Config.ALLOCATION_METHOD,
                    "risk_ratio": config.Config.RISK_RATIO
                }
                subscribe_response = requests.post(url=subscribe_url, headers=headers, json=subscribe_payload)
                if subscribe_response.status_code != 200:
                    return None

                if refId is not None:
                    db_updated = Register.update_db(refId=refId, investor_account=investor_pamm_account_id)
                    if not db_updated:
                        print(f"Error in inserting referral data in DB, however account is created.")
                return True

        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None

    @staticmethod
    def update_db(refId, investor_account):
        referral_account_data = Register.get_account_id_from_refId(refId)
        if referral_account_data:  # ✅ If data is not empty
            referral_account_id = referral_account_data[0]['id']  # Get the first 'id'

            # get investor details
            investor_details = Register.get_investor_details(investor_account)
            referral_details = Register.get_investor_details(referral_account_id)

            if investor_details and referral_details:
                db_info = {
                    "id": int(investor_details.get("accountId")),
                    "pid": int(referral_details.get("accountId")),
                    "accountNumber": investor_details.get("accountNumber"),
                    "clientID": int(investor_details.get("clientId")),
                    "name": investor_details.get("name"),
                    "email": investor_details.get("email"),
                    "nickname": investor_details.get("nickname"),
                    "parentAccountNumber": referral_details.get("accountNumber"),
                    "parentClientID": int(referral_details.get("clientId")),
                    "refId": investor_details.get("accountId")
                }

                Register.insert_into_pamm_master(db_config=db_config, db_info=db_info)
                return True

    @staticmethod
    def get_investor_details(account_id):
        try:
            url = f"{config.Config.SEARCH_ACCOUNT}/{account_id}"
            account_response = sm.make_api_call("GET", url=url)
            if account_response.status_code != 200:
                return None
            account_data = account_response.json()
            account_number = account_data.get("accountNumber")
            client_id = account_data.get("clientId")
            if client_id:
                client_url = f"{config.Config.SEARCH_CLIENT}/{client_id}"
                client_response = sm.make_api_call("GET", url=client_url)
                if client_response.status_code != 200:
                    return None
                client_data = client_response.json()
                name = client_data.get("name", "Not Defined")
                email = client_data.get("email", "Not Defined")
                nickname = client_data.get("nickname", "Not Defined")
                account_info = {
                    "accountId": account_id,
                    "accountNumber": account_number,
                    "clientId": client_id,
                    "name": name,
                    "email": email,
                    "nickname": nickname,
                }
                return account_info

        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None


    @staticmethod
    def get_account_id_from_refId(refId):
        conn = mysql.connector.connect(**db_config)
        try:
            with conn.cursor(dictionary=True) as cursor:
                # ✅ Fix: Use parameterized query safely
                query = "SELECT id FROM pamm_master where refId = %s"
                cursor.execute(query, (refId,))

                # ✅ Fetch valid data
                data = cursor.fetchall()

            # ✅ Return only the matching accounts
            return data if data else None
        finally:
            conn.close()  # Close the connection properly


    @staticmethod
    def insert_into_pamm_master(db_config, db_info):
        """
        Inserts data into the `pamm_master` table safely using parameterized query.

        :param db_config: Dictionary containing MySQL connection details.
        :param db_info: Dictionary containing values to insert.
        """
        query = """
            INSERT INTO pamm_master (
                id, pid, accountNumber, clientID, name, email, nickname, 
                parentAccountNumber, parentClientID, refId
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            db_info["id"],
            db_info["pid"],
            db_info["accountNumber"],
            db_info["clientID"],
            db_info["name"],
            db_info["email"],
            db_info["nickname"],
            db_info["parentAccountNumber"],
            db_info["parentClientID"],
            db_info["refId"]
        )

        conn = mysql.connector.connect(**db_config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()  # ✅ Commit the transaction
                print("✅ Data inserted successfully.")
        except mysql.connector.Error as err:
            print(f"❌ Error: {err}")
        finally:
            conn.close()  # ✅ Ensure the connection is closed properly


