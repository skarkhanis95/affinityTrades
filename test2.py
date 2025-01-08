import json
import pandas as pd

with open("accounts_data.json", "r") as accounts_file:
    accounts_data = json.load(accounts_file)

with open("clients_data.json", "r") as client_file:
    clients_data = json.load(client_file)

master_data = []

for account in accounts_data:
    if account.get("group", {}).get("id") == 16:
        accountNumber = account.get("accountNumber")
        accountId = account.get("accountId")
        clientID = account.get("clientId")
        productName = account.get("product", {}).get("name")
        acct = {
            "accountNumber": accountNumber,
            "accountId": accountId,
            "clientID": clientID,
            "productName": productName

        }
        master_data.append(acct)

# Lookup and enrich master_data
for entry in master_data:
    client_id = entry.get('clientID')  # Get clientID from master_data

    # Find the client in clients_data using clientId
    client = next((client for client in clients_data if client["clientId"] == client_id), None)

    if client:
        # Add firstName, lastName, name, email to the master_data entry
        entry['firstName'] = client['firstName']
        entry['lastName'] = client['lastName']
        entry['name'] = client['name']
        entry['email'] = client['email']
        entry['nickname'] = client['nickname']

# Resulting master_data after the update
print(master_data)
df = pd.DataFrame(master_data)
df.to_csv("pamm_investor_data.csv", index=False)