import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
from app.utils.org_chart import get_child_accounts, get_master_account
from app.models.wallets import Wallets
from app.utils.logger import logger
import config
import requests
from flask import session as flask_session, jsonify
from datetime import datetime
import pandas as pd
from app.models.backend_service import Backend
import mysql.connector
db_config = {
    "host": config.Config.DB_HOST,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}

class Organization:
    @staticmethod
    def get_org_tree_info(master_account_number,master_account_id):
        try:
            pamm_master_data = get_child_accounts(master_account_id)
            if pamm_master_data is None:
                # TODO
                # Return No Child Accounts logic to display single node chart attribute
                return {}

            # Get Transactions:
            transactions_data = Wallets.fetch_transactions()
            if transactions_data is None:
                # TODO
                # Return No Child Accounts logic to display single node chart attribute
                # implement seprate function to return just the logged in Account and show that in chart
                return {}

            for pamm_account in pamm_master_data:
                account_number = pamm_account['accountNumber']  # Current account number from pamm_master

                # Step 3: Filter transactions matching the current account_number in the loop
                total_fee = 0
                for transaction in transactions_data["data"]:
                    # Check if transaction type is "Partnership Fees" and the account number matches
                    if transaction.get('type') == 'Partnership Fees' and transaction.get('debitDetails', {}).get('account', {}).get('accountNumber') == account_number:
                        amount = transaction.get('debitDetails', {}).get("amount", 0)
                        total_fee += float(amount)  # Add amount to the total sum for this account

                # Step 4: Store the calculated sum (partnershipFees) back into the pamm_master data
                pamm_account['partnershipFees'] = round(total_fee, 2)

            for pamm_account in pamm_master_data:
                account_id = pamm_account["accountId"]
                pamm_account["balance"] = Organization.get_available_balance_from_account(account_id)

            total_partnership_fee_recevied = 0
            for pamm_account in pamm_master_data:
                partner_fee = pamm_account.get("partnershipFees")
                if partner_fee:
                    total_partnership_fee_recevied += round(float(partner_fee), 2)
                pamm_account["balanceLabel"] = "Balance"
                pamm_account["partnershipLabel"] = "Partnership Fee"

            # Add tags
            for pamm_account in pamm_master_data:
                tags = []
                if pamm_account["balance"] == 0:
                    tags.append("zero")
                # Any other tags go here
                pamm_account["tags"] = tags



            parent_account = get_master_account(master_account_number)
            if parent_account:
                parent_account[0]["partnershipFees"] = round(total_partnership_fee_recevied, 2)
                parent_account[0]["partnershipLabel"] = "Total $ Earned"
                parent_account_id = parent_account[0]["accountId"]
                parent_balance = round(Organization.get_available_balance_from_account(parent_account_id),2)
                parent_account[0]["balance"] = parent_balance

            # sum child nodes
            balance_sum = sum(item["balance"] for item in pamm_master_data if "pid" in item and item["pid"] == parent_account_id)
            current_parent_level = -1
            if parent_balance >= config.Config.LEVEL_0:
                current_parent_level = 0

                if config.Config.LEVEL_1 <= balance_sum <= config.Config.LEVEL_2:
                    current_parent_level = 1
                elif config.Config.LEVEL_2 <= balance_sum <= config.Config.LEVEL_3:
                    current_parent_level = 2
                elif balance_sum >= config.Config.LEVEL_3:
                    current_parent_level = 3
            level_name = f"LEVEL_{current_parent_level}_NAME"
            parent_account[0]["level"] = f"{getattr(config.Config, level_name, 'DefaultValue')}"
            parent_tags = ["parent"]
            parent_account[0]["tags"] = parent_tags


            if parent_account and parent_account is not None:
                pamm_master_data.insert(0, parent_account[0])


            for account in pamm_master_data:
                if 'accountId' in account:  # Check if 'accountId' exists in the dictionary
                    account['id'] = account.pop('accountId')




            #print(json.dumps(pamm_master_data))
            return pamm_master_data
        except Exception as e:
            logger.error("Error in get_org_tree_info: %s", str(e))
            return {}


    @staticmethod
    def get_available_balance_from_account(account_id):
        try:
            account_data = Backend.get_account_info(account_id)
            if account_data is None:
                print("Error in fetching account information")
                return 0.00

            available_balance = float(account_data.get("statement", {}).get("availableBalance"))
            # formatted_balance = "{:,.2f}".format(available_balance)
            formatted_balance = round(available_balance, 2)
            return formatted_balance
        except Exception as e:
            logger.error("Error in get_available_balance_from_account: %s", str(e))
            return 0.00

    @staticmethod
    def validate_accounts_in_referral(pamm_accounts):
        """
        Validates the accounts in pamm_accounts against the database.
        Returns only the accounts that exist in the database.
        """
        # ✅ Fix: Extract account IDs properly
        accounts = [acc.get("accountId") for acc in pamm_accounts if "accountId" in acc]

        # ✅ Fix: Handle empty accounts case
        if not accounts:
            return []

        conn = mysql.connector.connect(**db_config)
        try:
            with conn.cursor(dictionary=True) as cursor:
                # ✅ Fix: Use parameterized query safely
                query = f"SELECT * FROM pamm_master WHERE id IN ({', '.join(['%s'] * len(accounts))})"
                cursor.execute(query, tuple(accounts))
                # ✅ Fetch valid data
                data = cursor.fetchall()
            # ✅ Validate and filter accounts
            valid_accounts = Organization.validate_accounts(accounts, data)
            test = [acc for acc in pamm_accounts if acc.get("accountId") in valid_accounts]
            # ✅ Return only the matching accounts
            return [acc for acc in pamm_accounts if acc.get("accountId") in valid_accounts]
        except Exception as e:
            logger.error("Database error in validate_accounts_in_referral: %s", str(e))
            return []
        finally:
            conn.close()  # Close the connection properly

    @staticmethod
    def validate_accounts(accounts, data_from_db):
        """
        Compares the list of accounts passed vs the ones actually found in the DB.
        Returns only the IDs that exist in the database.

        :param accounts: List of account IDs passed in the request
        :param data_from_db: List of dictionaries containing the fetched data from DB
        :return: List of IDs that exist in the DB
        """
        # ✅ Extract valid IDs from the database result
        db_ids = {row["id"] for row in data_from_db}

        # ✅ Return only matching account IDs
        return list(db_ids.intersection(accounts))

    @staticmethod
    def get_referral_data(accountId):
        """
        Validates the accounts in pamm_accounts against the database.
        Returns only the accounts that exist in the database.
        """


        conn = mysql.connector.connect(**db_config)
        try:
            with conn.cursor(dictionary=True) as cursor:
                # ✅ Fix: Use parameterized query safely
                query = "SELECT id, accountNumber, name, refId FROM pamm_master where id = %s"
                cursor.execute(query, (accountId,))

                # ✅ Fetch valid data
                data = cursor.fetchall()

            # ✅ Return only the matching accounts
            return data
        except Exception as e:
            logger.error("Database error in get_referral_data: %s", str(e))
        finally:
            conn.close()  # Close the connection properly






