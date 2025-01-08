import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session
from datetime import datetime
from app.models.wallets import Wallets


class Funds:
    @staticmethod
    def get_deposit_info():
        try:
            # Get Wallets and Transactions from their models
            wallets_data = Wallets.fetch_wallets_info()


            #Get Deposit Methods
            url = config.Config.GET_DEPOSIT_METHODS_API
            response = make_authenticated_request("GET", url)
            if response.status_code != 200:
                return None
            deposit_methods = response.json()["data"]

            #Prepare ALl the required data
            deposit_data = {}
            accounts = []

            # Get eWallets
            for wallet in wallets_data["data"]:

                if wallet.get("platform", {}).get("id") == 1 \
                        and wallet["platform"].get("caption") == "eWallet" \
                        and wallet["platform"].get("isDemo") is False \
                        and wallet.get("group", {}).get("name") == "Fiat":

                    name = wallet.get("caption")
                    number = wallet.get("accountNumber")
                    accountId = wallet.get("accountId")
                    acccount_obj = {
                        "name": name,
                        "number": number,
                        "accountId": accountId
                    }
                    accounts.append(acccount_obj)


            # get deposit methods
            alphabetic_codes = [
                currency["currency"]["alphabeticCode"]
                for entry in deposit_methods
                for currency in entry.get("paymentSystemCurrencies", [])
            ]

            # Get Currency Rates
            currency_rates = {}
            for entry in deposit_methods:
                for currency in entry.get("paymentSystemCurrencies", []):
                    alphabetic_code = currency["currency"]["alphabeticCode"]
                    numeric_code = currency["currency"]["numericCode"]
                    rate = Funds.get_currency_rate(numeric_code)
                    currency_rates[alphabetic_code] = rate

            # Add currencies to accounts
            for account in accounts:
                account["currencies"] = alphabetic_codes

            # # Get Payment Methds
            # payment_methods = {}
            # for entry in deposit_methods:
            #     parent_caption = entry["caption"]
            #     for currency in entry.get("paymentSystemCurrencies", []):
            #         alphabetic_code = currency["currency"]["alphabeticCode"]
            #         # Append the parent caption as the payment method
            #         if alphabetic_code not in payment_methods:
            #             payment_methods[alphabetic_code] = []
            #         payment_methods[alphabetic_code].append(parent_caption)
            #
            # # Get Numeric Payment Methods:
            # payment_methods2 = {}
            # for entry in deposit_methods:
            #     parent_id = entry["id"]
            #     for currency in entry.get("paymentSystemCurrencies", []):
            #         alphabetic_code = currency["currency"]["alphabeticCode"]
            #         # Append the parent caption as the payment method
            #         if alphabetic_code not in payment_methods:
            #             payment_methods2[alphabetic_code] = parent_id
            consolidated_data = {}

            for entry in deposit_methods:
                parent_id = entry["id"]
                parent_caption = entry["caption"]

                for currency in entry.get("paymentSystemCurrencies", []):
                    alphabetic_code = currency["currency"]["alphabeticCode"]
                    currency_id = currency["currency"]["numericCode"]

                    # Create or update the consolidated data structure
                    if alphabetic_code not in consolidated_data:
                        consolidated_data[alphabetic_code] = {
                            "currency_id": currency_id,
                            "payment_methods": []
                        }

                    consolidated_data[alphabetic_code]["payment_methods"].append({
                        "id": parent_id,
                        "caption": parent_caption
                    })

            #print(consolidated_data)

            # Create Final Object
            deposit_data = {
                "accounts": accounts,
                "rates": currency_rates,
                "consolidated": consolidated_data
            }
            #print(deposit_data)
            return deposit_data


        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None


    @staticmethod
    def get_currency_rate(numeric_code):
        try:
            url = f"https://api.affinitytrades.com/api/v1/rates/{numeric_code}/{config.Config.USD_CURRENCY_CODE}?spread=1"
            response = make_authenticated_request("GET", url=url)
            if response.status_code != 200:
                return None
            data = response.json()
            rate = data.get("data", {}).get("rate", {}).get("value", 0)
            return rate
        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None


    @staticmethod
    def get_transfer_info():
        try:
            wallets_data = Wallets.fetch_wallets_info()
            accounts = []
            for wallet in wallets_data["data"]:
                acc = {
                "accountId" : int(wallet.get("accountId", "")),
                "accountNumber": wallet.get("accountNumber", ""),
                "accountName": wallet.get("caption"),
                "availableBalance": round(float(wallet.get("statement", {}).get("availableBalance", 0)), 2),
                "type":wallet.get("platform", {}).get("caption", "")
                }
                accounts.append(acc)

            transfer_data = {
                "accounts": accounts
            }
            return transfer_data
        except Exception as e:
            print(f"Error occured in getting Transfer Deails: {e}")
            return None

