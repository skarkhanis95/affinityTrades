import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
from app.utils.org_chart import get_child_accounts, get_master_account
from app.models.wallets import Wallets
import config
import requests
from flask import session as flask_session
from datetime import datetime
from app.models.backend_service import Backend

class Organization:
    @staticmethod
    def get_org_tree_info(master_account_number,master_account_id):
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
            pamm_account['partnershipFees'] = total_fee

        for pamm_account in pamm_master_data:
            account_id = pamm_account["accountId"]
            pamm_account["balance"] = Organization.get_available_balance_from_account(account_id)

        parent_account = get_master_account(master_account_number)
        pamm_master_data.insert(0, parent_account[0])
        for account in pamm_master_data:
            if 'accountId' in account:  # Check if 'accountId' exists in the dictionary
                account['id'] = account.pop('accountId')

        return pamm_master_data


    @staticmethod
    def get_available_balance_from_account(account_id):

        account_data = Backend.get_account_info(account_id)
        if account_data is None:
            print("Error in fetching account information")
            return "0.00"

        available_balance = float(account_data.get("statement", {}).get("availableBalance"))
        formatted_balance = "{:,.2f}".format(available_balance)
        return formatted_balance






