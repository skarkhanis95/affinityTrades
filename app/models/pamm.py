import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session
from datetime import datetime
from app.models.wallets import Wallets
from urllib.parse import urlencode


class PAMM:
    @staticmethod
    def get_accounts_info():
        try:
            # Get Wallets and Transactions from their models
            accounts = []
            wallets_data = Wallets.fetch_wallets_info()
            # Get PAMM Accounts
            for wallet in wallets_data["data"]:

                if wallet.get("platform", {}).get("id") == 2 \
                        and wallet["platform"].get("caption") == "MT5Live" \
                        and wallet["platform"].get("isDemo") is False \
                        and wallet.get("group", {}).get("name") == "PAMM Investor Account":
                    name = wallet.get("caption")
                    number = wallet.get("accountNumber")
                    accountId = wallet.get("accountId")
                    balance = float(round(wallet.get("statement", {}).get("availableBalance", 0.00), 2))
                    currency = wallet.get("currency", {}).get("alphabeticCode", "NaN")
                    acccount_obj = {
                        "name": name,
                        "number": number,
                        "accountId": accountId,
                        "balance": balance,
                        "currency": currency
                    }
                    accounts.append(acccount_obj)

            #Get INVESTMENT ACCOUNTS
            url = config.Config.INVESTMENT_ACCOUNTS_API
            response = make_authenticated_request("GET", url)
            if response.status_code != 200:
                return None
            investment_accounts_data = response.json()["data"]
            investment_accounts = []

            account_ids = []
            for acc in investment_accounts_data:

                account_ids.append(acc.get("accountId"))


            # Build URL for balance & equity
            investment_platform_id = 1
            # Start the base URL
            base_url = "https://api.affinitytrades.com/api/v1/investment/common/accounts"
            bl_uri = "/get_balance_and_equity_by_ids"

            # Create a dictionary for the query parameters
            query_params = {
                "investment_platform_id": investment_platform_id
            }

            # Add account_ids dynamically to the query parameters
            for idx, account_id in enumerate(account_ids):
                query_params[f"account_ids[{idx}]"] = account_id

            # Create the final query string using urlencode
            query_string = urlencode(query_params, doseq=True)

            # Combine the base URL with the query string
            final_url = f"{base_url}{bl_uri}?{query_string}"


            response = make_authenticated_request("GET", url=final_url)
            if response.status_code != 200:
                return None

            balance_equity_accounts = response.json()["data"]


            for investment_account in investment_accounts_data:
                subscriptionCount = int(investment_account.get("subscriptionsCount"))

                if subscriptionCount > 0:
                    subscriptionStatus = "Subscribed"
                else:
                    subscriptionStatus = "Unsubscribed"

                account = next((acc for acc in accounts if acc["accountId"] == investment_account["id"]), None)
                be_acc = next((acc for acc in balance_equity_accounts if acc["account_id"] == investment_account["accountId"]), None)
                if account and be_acc:
                    acc = {
                        "id": investment_account.get("id"),
                        "accountId": investment_account.get("accountId"),
                        "accountName": investment_account.get("accountName"),
                        "subscriptionStatus": subscriptionStatus,
                        "profit": investment_account.get("profit"),
                        "maxDD": investment_account.get("maxDD"),
                        "currency": account["currency"],
                        "balance": be_acc["balance"],
                        "equity": be_acc["equity"]
                    }
                    investment_accounts.append(acc)



            # Create Final Object
            pamm_data = {
                "accounts": investment_accounts,
            }

            return pamm_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None
