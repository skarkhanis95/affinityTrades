import base64
import json
import os
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session
from datetime import datetime



class Wallets:
    @staticmethod
    def fetch_wallets_info():
        """Fetch user profile information and handle photo processing."""
        try:
            url = config.Config.ACCOUNTS_API
            # Make an API call to fetch profile data
            response = make_authenticated_request("GET", url)

            if response.status_code != 200:
                return None
            wallets_data = response.json()

            # Filter out wallets with platform.isDemo = True
            wallets_data['data'] = [wallet for wallet in wallets_data['data'] if
                                    not wallet['platform'].get('isDemo', False)]

            for wallet in wallets_data['data']:
                if wallet['platform'].get('isDemo', False):
                    continue  # Skip this wallet if it's a demo account
                current_balance = float(wallet['statement']['currentBalance'])
                available_balance = float(wallet['statement']['availableBalance'])
                hold_balance = float(wallet['statement']['hold'])

                # Format each balance to 2 decimal places
                wallet['statement']['currentBalance'] = round(current_balance, 2)
                wallet['statement']['availableBalance'] = round(available_balance, 2)
                wallet['statement']['hold'] = round(hold_balance, 2)

            # add totals of current balance
            total_balances = []
            for wallet in wallets_data['data']:
                if wallet['platform'].get('isDemo', False):
                    continue  # Skip this wallet if it's a demo account
                current_balance = float(wallet['statement']['currentBalance'])
                total_balances.append(current_balance)
                # wallet['statement']['currentBalance'] = round(current_balance, 2)

            total_balance = sum(total_balances)
            formatted_balance = format(total_balance, ",.2f")
            inrBalance = total_balance * config.Config.WITHDRAWL_INR_USD_RATE
            formatted_inr_balance = format(inrBalance, ",.2f")

            #update wallets data object to include additional fields
            wallets_data["totalEstBalance"] = formatted_balance
            wallets_data["inrEstBalance"] = formatted_inr_balance
            wallets_data["conversionRate"] = config.Config.WITHDRAWL_INR_USD_RATE


            return wallets_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching wallets data: {e}")
            return None

    @staticmethod
    def fetch_transactions():
        try:

            transaction_url = config.Config.TRANSACTIONS_API
            transaction_response = make_authenticated_request("GET", transaction_url)
            if transaction_response.status_code != 200:
                return None
            transactions_data = transaction_response.json()
            try:
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))

                # Temporary create Database and store information here:
                # Local Server Settings
                # file_path = os.path.join(BASE_DIR, '../daily_files/accounts_data.json')
                # file_path2 = os.path.join(BASE_DIR, '../daily_files/clients_data.json')
                # Remote Server Settings
                file_path = '/home/affinitytrades2024/mysite/affinityTrades/app/daily_files/accounts_data.json'
                file_path2 = '/home/affinitytrades2024/mysite/affinityTrades/app/daily_files/clients_data.json'
                # Ensure the directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'r') as file:
                    accounts_data = json.load(file)
                with open(file_path2, 'r') as file2:
                    clients_data = json.load(file2)

                clients_dict = {client['clientId']: client['name'] for client in clients_data}
                # Create a dictionary for fast lookup of account details based on accountId
                accounts_dict = {account['accountId']: account['clientId'] for account in accounts_data}

                for transaction in transactions_data["data"]:
                    # Handle creditDetails account
                    if transaction.get("creditDetails") is None and transaction["type"] == "withdrawal":
                        withdraw_amt = transaction.get("debitDetails", {}).get("amount")
                        transaction["creditDetails"] = {
                                "account": {
                                "accountId": 000,
                                "accountNumber": "000",
                                "clientName": "Bank Withdrawl"
                            },
                            "amount": withdraw_amt
                        }

                    else:
                        credit_account_id = transaction.get("creditDetails", {}).get("account", {}).get("accountId")
                        if credit_account_id and credit_account_id in accounts_dict:
                            client_id = accounts_dict[credit_account_id]
                            transaction["creditDetails"]["account"]["clientName"] = clients_dict.get(client_id, "Unknown")

                    # Handle debitDetails account
                    if transaction.get("debitDetails") is None and transaction["type"] == "deposit":
                        # Initialize debitDetails and assign values
                        transaction["debitDetails"] = {"account": {"clientName": "Bank Deposit (Self)"}}

                    else:
                        debit_account_id = transaction.get("debitDetails", {}).get("account", {}).get("accountId")
                        if debit_account_id and debit_account_id in accounts_dict:
                            client_id = accounts_dict[debit_account_id]
                            transaction["debitDetails"]["account"]["clientName"] = clients_dict.get(client_id,
                                                                                                    "Unknown")

                    #modify transaction types
                    if transaction["type"] == "fees" and transaction['creditDetails']['account']['accountNumber'] == "129":
                        transaction["type"] = "Performance Fees"

            except AttributeError as e:
                print(e)
                raise

            wallets_data = Wallets.fetch_wallets_info()
            self_wallets = []
            for wallet in wallets_data["data"]:
                self_wallets.append(wallet["accountNumber"])

            for transaction in transactions_data["data"]:
                if transaction.get("debitDetails") and transaction["debitDetails"].get("account") and \
                        transaction["debitDetails"]["account"].get("accountNumber"):
                    account_number = transaction["debitDetails"]["account"]["accountNumber"]
                    if account_number is not None and account_number not in self_wallets:
                        # Proceed with your logic for the transaction
                        transaction["type"] = "Partnership Fees"

            # Calculate Total Deposits
            total_deposits = 0
            for transaction in transactions_data["data"]:
                if transaction.get("type") == "deposit":
                    amount = float(transaction.get("creditDetails", {}).get("amount", 0))
                    total_deposits += amount

            total_deposits_for_waa = []
            for transaction in transactions_data["data"]:
                if transaction.get("type") == "deposit":
                    amount = float(transaction.get("creditDetails", {}).get("amount", 0))
                    createTime = transaction.get("createTime")
                    d = {
                        "amount": amount, "createTime": createTime
                    }
                    total_deposits_for_waa.append(d)


            partnership_fees = Wallets.sum_partnership_fees(transactions_data["data"])
            performance_fees = Wallets.sum_performance_fees_on_first_of_month(transactions_data["data"])
            total_profit = round(performance_fees * 2, 2)
            individual_profit = round(performance_fees, 2)
            total_returns_percentage = round((total_profit / total_deposits) * 100, 2) if total_deposits != 0 else 0
            individual_returns_percentage = round((individual_profit / total_deposits) * 100, 2) if total_deposits !=0 else 0
            annual_returns = round(Wallets.annualized_return(total_deposits, individual_profit, total_deposits_for_waa),2)
            cagr = round(Wallets.calculate_cagr(total_deposits, individual_profit, total_deposits_for_waa),2)

            transactions_data["totalProfit"] = total_profit
            transactions_data["individualProfit"] = individual_profit
            transactions_data["partnershipFees"] = partnership_fees

            conversion_rate = config.Config.WITHDRAWL_INR_USD_RATE
            # INR data
            transactions_data["totalProfitINR"] = round(total_profit * conversion_rate)
            transactions_data["individualProfitINR"] = round(individual_profit * conversion_rate)
            transactions_data["partnershipFeesINR"] = round(partnership_fees * conversion_rate)
            transactions_data["conversionRate"] = conversion_rate

            #Add Returns
            transactions_data["totalReturns"] = total_returns_percentage
            transactions_data["individualReturns"] = individual_returns_percentage
            transactions_data["annualReturns"] = annual_returns
            transactions_data["cagr"] = cagr
            #print(json.dumps(transactions_data))

            return transactions_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions data: {e}")
            return None


    @staticmethod
    def sum_partnership_fees(transactions):
        total_fees = 0  # Initialize the sum for the partnership fees

        # Loop through all the transactions
        for transaction in transactions:
            # Check if the transaction type is 'Partnership Fees'
            if transaction.get("type") == "Partnership Fees":
                # Check if the 'amount' exists and add it to the total
                amount = float(transaction.get("creditDetails", {}).get("amount", 0))  # Ensure it's a float
                total_fees += amount  # Add to the running total

        return round(total_fees,2)

    @staticmethod
    def sum_performance_fees_on_first_of_month(transactions):
        total_fees = 0  # Initialize the sum for the performance fees

        # Loop through all the transactions
        for transaction in transactions:
            # Check if the transaction type is 'Performance Fee'
            if transaction.get("type") == "Performance Fees":

                # Check if the 'date' exists and if it's the 1st of the month
                date_str = transaction.get("createTime")
                if date_str:
                    try:
                        # Parse the date string into a datetime object
                        transaction_date = datetime.fromisoformat(date_str)  # Assuming ISO format 'YYYY-MM-DDTHH:MM:SS'

                        if transaction_date.day == 1:  # Check if it's the 1st of the month

                            amount = float(transaction.get("creditDetails", {}).get("amount", 0))  # Ensure it's a float
                            total_fees += amount  # Add to the running total
                    except ValueError:
                        # If date is not in valid format, skip this transaction
                        pass

        return total_fees


    @staticmethod
    def days_since(date_str):
        deposit_date = datetime.fromisoformat(date_str[:-6])  # Remove timezone (+00:00)
        today = datetime.utcnow()
        return (today - deposit_date).days

    @staticmethod
    def weighted_average_age(deposits):
        total_weighted_days = sum(d["amount"] * Wallets.days_since(d["createTime"]) for d in deposits)
        total_deposit = sum(d["amount"] for d in deposits)
        return total_weighted_days / total_deposit if total_deposit !=0 else 0

    @staticmethod
    def annualized_return(total_deposit, total_profit, deposits):
        waa = Wallets.weighted_average_age(deposits)
        return ((total_profit / total_deposit) * 100 * (365 / waa) ) if total_deposit !=0 else 0

    @staticmethod
    def calculate_cagr(total_deposit, total_profit, deposits):
        final_value = total_deposit + total_profit
        initial_value = total_deposit
        waa_days = Wallets.weighted_average_age(deposits)
        t_years = waa_days / 365  # Convert days to years

        cagr = (final_value / initial_value) ** (1 / t_years) - 1
        return cagr * 100 if total_deposit !=0 else 0  # Convert to percentage