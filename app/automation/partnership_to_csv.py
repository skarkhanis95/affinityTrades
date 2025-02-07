import json
import pandas as pd

# Load the JSON file
json_file_path = "final_hierarchy_analysis.json"

with open(json_file_path, "r") as file:
    data = json.load(file)

# Flatten JSON data into a CSV-friendly format
flattened_data = []

for entry in data:
    base_info = {
        "accountId": entry["accountId"],
        "accountNumber": entry.get("accountNumber", "N/A"),
        "clientID": entry.get("clientID", "N/A"),
        "name": entry.get("name", "N/A"),
        "email": entry.get("email", "N/A"),
        "nickname": entry.get("nickname", ""),
        "parentAccountNumber": entry.get("parentAccountNumber", "N/A"),
        "parentClientID": entry.get("parentClientID", "N/A"),
        "balance": entry["balance"],
    }

    # Process receivingFromAccounts
    for receiving in entry.get("receivingFromAccounts", []):
        row = base_info.copy()
        row["receivingFromAccountId"] = receiving["accountId"]
        row["receivingFromPercentage"] = receiving["percentage"]
        flattened_data.append(row)

    # Process givingToAccounts
    for giving in entry.get("givingToAccounts", []):
        row = base_info.copy()
        row["givingToAccountId"] = giving["accountId"]
        row["givingToAccountNumber"] = giving["accountNumber"]
        row["givingToPercentage"] = giving["percentage"]
        flattened_data.append(row)

    # If no receiving or giving accounts, just add base info
    if not entry.get("receivingFromAccounts") and not entry.get("givingToAccounts"):
        flattened_data.append(base_info)

# Convert to DataFrame
df = pd.DataFrame(flattened_data)

# Save to CSV
csv_file_path = "sample_heir_data.csv"
df.to_csv(csv_file_path, index=False)

