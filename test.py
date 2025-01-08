import requests
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

# MySQL connection setup










# Function to fetch and store data with pagination (API call handling)
# Function to fetch and store data with pagination (API call handling)
def fetch_and_store_data(api_url, limit=100, offset=0):
    total = 1  # Start with a non-zero value for total

    clients_data = []
    accounts_data = []

    while offset < total:
        # Fetch data from the API with pagination
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzYzMjc4ODcsIm5iZiI6MTczNjMyNzg4NywiZXhwIjoxNzM2MzI4NDg3LCJpc3MiOiJodHRwczovL2FwaS5hZmZpbml0eXRyYWRlcy5jb20iLCJzdWIiOiIyOCIsImlhdF9tdCI6IjE3MzYzMjc4ODcuNjk2NCJ9.en8rKJqURuZz37pj7xgWcK5P1AzPA5r3xZPAkpa4imoHTguAliM4kY6v6ZORlo0Gyy2Nyj4pPlQjFQ8BNbBqPP4ZLb_UDXouTR6ZguU95FC3ljDXVwjOaiEPwupds8Qij-HaGvzZjCr2d8E639qZox3c6xp5MJhTEgiaCeb0DJZDG_lMmctOEJW-5PlWI41Ho1VeQCld9m4oUM1Cfr-eqzZr2nK5zobeY581jY7PO6lah3zPJKwYrrWlylWxLsfrfMZjn6Bij292ekZF5zeyBAf9vtn3XqsbUkMkt9iYecAhPQ5YiC8uazJjIYt-tYsxop8oZBp5CIYfB4b9QCMcVw'
        }
        response = requests.get(f"{api_url}?limit={limit}&offset={offset}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            clients = response.json()["data"]
            for client in clients:
                clients_data.append(client)


            total = data.get('total', 0)
            offset += limit
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break
    filename = "clients_data.json"
    with open(filename, 'w') as json_file:
        # Write the clients data as a JSON array to the file
        json.dump(clients_data, json_file, indent=4)
    print("file created")

if __name__ == "__main__":
    # API URLs (replace with actual URLs for clients and accounts)
    clients_api_url = "https://api.affinitytrades.com/api/v2/clients"
    accounts_api_url = "https://api.affinitytrades.com/api/v2/accounts"

    # Fetch and store client data
    fetch_and_store_data(clients_api_url)

    # Fetch and store account data
    # fetch_and_store_data(accounts_api_url)
