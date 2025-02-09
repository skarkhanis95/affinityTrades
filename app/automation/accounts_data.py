import requests
import json
from app.services.service_account_manager import ServiceAccountManager


sm = ServiceAccountManager()


def fetch_and_store_data(api_url, limit=100, offset=0, type=""):
    total = 1  # Start with a non-zero value for total

    return_data = []
    accounts_data = []

    while offset < total:
        # Fetch data from the API with pagination
        #response = requests.get(f"{api_url}?limit={limit}&offset={offset}", headers=headers)
        response = sm.make_api_call("GET", url=f"{api_url}?limit={limit}&offset={offset}")

        if response.status_code == 200:
            data = response.json()
            objects = response.json()["data"]
            for object in objects:
                return_data.append(object)


            total = data.get('total', 0)
            offset += limit
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break
    if type == "accounts":
        filename = '/home/affinitytrades2024/mysite/affinityTrades/app/daily_files/accounts_data.json'
    elif type == "clients":
        filename = '/home/affinitytrades2024/mysite/affinityTrades/app/daily_files/clients_data.json'
    with open(filename, 'w') as json_file:
        # Write the clients data as a JSON array to the file
        json.dump(return_data, json_file, indent=4)
    #print(json.dumps(return_data))
    #print("file created")






urls = [
    {"url": "https://api.affinitytrades.com/api/v2/clients", "type": "clients"},
    {"url": "https://api.affinitytrades.com/api/v2/accounts", "type": "accounts"}
]
# Fetch and store client data

for url in urls:
    fetch_and_store_data(url["url"],type=url["type"])