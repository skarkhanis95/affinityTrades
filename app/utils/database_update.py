import requests
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

# MySQL connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="affinity_db_user",  # Replace with your MySQL username
        password="whisky3115",  # Replace with your MySQL password
        database="affinityTrades"  # Replace with your MySQL database name
    )


def convert_to_mysql_date(date_str):
    if date_str is None:
        return None  # Return None if the input is None
    try:
        # Ensure date_str is a string before passing to fromisoformat
        if isinstance(date_str, str):
            return datetime.fromisoformat(date_str).date()  # Convert to date (YYYY-MM-DD)
        else:
            return None  # Return None if the input is not a string
    except ValueError:
        return None  # If the date format is invalid, return None

# Function to insert bulk client data into MySQL
# Function to insert bulk client data into MySQL
# Function to insert bulk client data into MySQL
def insert_clients_bulk(clients_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare the insert query for clients
        query = """
        INSERT INTO clients (client_id, name, first_name, last_name, email, birthday, status, risk_level, country, city)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name), first_name = VALUES(first_name), last_name = VALUES(last_name), email = VALUES(email),
        status = VALUES(status), risk_level = VALUES(risk_level), country = VALUES(country), city = VALUES(city), 
        updated_at = CURRENT_TIMESTAMP;
        """

        # Convert client data into tuples, ensuring proper alignment
        formatted_clients_data = []
        for client in clients_data:
            print(client)
            # Convert birthday to the correct format (YYYY-MM-DD)
            birthday = convert_to_mysql_date(client.get('birthday', None))  # Safely get and convert birthday
            client_data_tuple = (
                client['clientId'],
                client['name'],
                client['firstName'],
                client['lastName'],
                client['email'],
                birthday,
                client['status'],
                client['riskLevel'],
                client.get('country', ''),
                client.get('city', '')
            )
            formatted_clients_data.append(client_data_tuple)

        # Insert data only if there is valid data
        if formatted_clients_data:
            cursor.executemany(query, formatted_clients_data)  # Insert multiple records at once
            conn.commit()
            print(f"{cursor.rowcount} clients inserted or updated.")
        else:
            print("No valid client data to insert.")
    except Error as e:
        print(f"Error inserting clients: {e}")
    finally:
        cursor.close()
        conn.close()



# Function to insert bulk account data into MySQL
def insert_accounts_bulk(accounts_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare the insert query for accounts
        query = """
        INSERT INTO accounts (account_id, account_number, caption, client_id, currency_alphabetic_code, currency_name, currency_numeric_code, 
                              currency_minor_unit, group_name, platform_caption, platform_name, product_name, available_balance, current_balance, 
                              credit, equity, free_margin, hold, margin, margin_level, pnl, update_time, archive, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE
        caption = VALUES(caption), currency_alphabetic_code = VALUES(currency_alphabetic_code), currency_name = VALUES(currency_name),
        currency_numeric_code = VALUES(currency_numeric_code), currency_minor_unit = VALUES(currency_minor_unit), 
        group_name = VALUES(group_name), platform_caption = VALUES(platform_caption), platform_name = VALUES(platform_name), 
        product_name = VALUES(product_name), available_balance = VALUES(available_balance), current_balance = VALUES(current_balance),
        credit = VALUES(credit), equity = VALUES(equity), free_margin = VALUES(free_margin), hold = VALUES(hold), margin = VALUES(margin),
        margin_level = VALUES(margin_level), pnl = VALUES(pnl), update_time = VALUES(update_time), updated_at = CURRENT_TIMESTAMP;
        """

        formatted_accounts_data = []
        for account in accounts_data:
            account_data = (
                account['accountId'],
                account['accountNumber'],
                account['caption'],
                account['clientId'],
                account['currency']['alphabeticCode'],
                account['currency']['name'],
                account['currency']['numericCode'],
                account['currency']['minorUnit'],
                account['group']['name'],  # Corrected this line to access group name
                account['platform']['caption'],
                account['platform']['name'],
                account['product']['name'],
                account['statement']['availableBalance'],
                account['statement']['currentBalance'],
                account['statement']['credit'],
                account['statement']['equity'],
                account['statement']['freeMargin'],
                account['statement']['hold'],
                account['statement']['margin'],
                account['statement']['marginLevel'],
                account['statement']['pnl'],
                account['statement']['updateTime'],
                account.get('archive', 0)  # Defaulting to 0 if 'archive' is missing
            )

            # Debugging: Check the length of the data and compare it with the query placeholders
            if len(account_data) != 22:
                print(f"Error: Data for account {account['accountId']} has {len(account_data)} fields, expected 22")
            else:
                formatted_accounts_data.append(account_data)

        # Insert only if the data is correct
        if formatted_accounts_data:
            cursor.executemany(query, formatted_accounts_data)  # Insert multiple records at once
            conn.commit()
            print(f"{cursor.rowcount} accounts inserted or updated.")
        else:
            print("No valid data to insert.")

    except Error as e:
        print(f"Error inserting accounts: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to fetch and store data with pagination (API call handling)
# Function to fetch and store data with pagination (API call handling)
def fetch_and_store_data(api_url, data_type, limit=100, offset=0):
    total = 1  # Start with a non-zero value for total

    clients_data = []
    accounts_data = []

    while offset < total:
        # Fetch data from the API with pagination
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzU5ODg3NzYsIm5iZiI6MTczNTk4ODc3NiwiZXhwIjoxNzM1OTg5Mzc2LCJpc3MiOiJodHRwczovL2FwaS5hZmZpbml0eXRyYWRlcy5jb20iLCJzdWIiOiIyOCIsImlhdF9tdCI6IjE3MzU5ODg3NzYuODkyMyJ9.rvCsME5ebxyUz2kg9JFBIB9iuK7K1Que-i-uUAtywGPL15q4jxEbcT_CQGLSiZinagCXRY_I72XlLRDxKVgZK05mvHxhTLmgFeQ_0lNtYTlQo687iZtVnk7YkGgDGkOt0Ko3KDQmew7jbc1PQWY8_Pxlxm0_wry0scyrbHu09hfh_MmWspsZANSX6oK3_spWmyrw-V_BkkUy-ZZjRmDCO21e3CXMGOQ8n75-JyUNrS9QBOdr1_xtRfY0L97Ybq1ludNwkXM2B_B15ceWwvbATxD_2KvJRWfFos1YItSjvjc-anANuX7I5cUUQoO6jbK-ZUUdkTQqebxgyBkFK1shPg'
            }
        response = requests.get(f"{api_url}?limit={limit}&offset={offset}", headers=headers)
        if response.status_code == 200:
            data = response.json()

            if data_type == "clients":
                for client in data['data']:
                    # Prepare client data for bulk insert, including all necessary fields
                    client_data = {
                        'clientId': client['clientId'],
                        'name': client['name'],
                        'firstName': client['firstName'],
                        'lastName': client['lastName'],
                        'email': client['email'],
                        'birthday': client.get('birthday', None),  # Safely get birthday
                        'status': client['status'],
                        'riskLevel': client['riskLevel'],
                        'country': client.get('country', ''),
                        'city': client.get('city', ''),
                        'createdAt': client.get('createdAt', None),  # Add createdAt field
                        'updatedAt': client.get('updatedAt', None)   # Add updatedAt field
                    }
                    clients_data.append(client_data)

            elif data_type == "accounts":
                for account in data['data']:
                    # Prepare account data for bulk insert, including all necessary fields
                    account_data = {
                        'accountId': account['accountId'],
                        'accountNumber': account['accountNumber'],
                        'caption': account['caption'],
                        'clientId': account['clientId'],
                        'currency_alphabetic_code': account['currency']['alphabeticCode'],
                        'currency_name': account['currency']['name'],
                        'currency_numeric_code': account['currency']['numericCode'],
                        'currency_minor_unit': account['currency']['minorUnit'],
                        'group_name': account['group']['name'],
                        'platform_caption': account['platform']['caption'],
                        'platform_name': account['platform']['name'],
                        'product_name': account['product']['name'],
                        'available_balance': account['statement']['availableBalance'],
                        'current_balance': account['statement']['currentBalance'],
                        'credit': account['statement']['credit'],
                        'equity': account['statement']['equity'],
                        'free_margin': account['statement']['freeMargin'],
                        'hold': account['statement']['hold'],
                        'margin': account['statement']['margin'],
                        'margin_level': account['statement']['marginLevel'],
                        'pnl': account['statement']['pnl'],
                        'update_time': account['statement']['updateTime'],
                        'archive': account.get('archive', 0),  # Default to 0 if archive is not present
                        'createdAt': account.get('createdAt', None),  # Add createdAt field
                        'updatedAt': account.get('updatedAt', None)   # Add updatedAt field
                    }
                    accounts_data.append(account_data)

            # Perform bulk insert after collecting data
            if data_type == "clients" and clients_data:
                insert_clients_bulk(clients_data)
                clients_data = []  # Reset for next page of data

            if data_type == "accounts" and accounts_data:
                insert_accounts_bulk(accounts_data)
                accounts_data = []  # Reset for next page of data

            total = data.get('total', 0)
            offset += limit
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break



if __name__ == "__main__":
    # API URLs (replace with actual URLs for clients and accounts)
    clients_api_url = "https://api.affinitytrades.com/api/v2/clients"
    accounts_api_url = "https://api.affinitytrades.com/api/v2/accounts"

    # Fetch and store client data
    fetch_and_store_data(clients_api_url, "clients")

    # Fetch and store account data
    #fetch_and_store_data(accounts_api_url, "accounts")
