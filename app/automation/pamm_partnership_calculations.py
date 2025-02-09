import mysql.connector
import json
import config

# Database Configuration


db_config = {
    "host": config.Config.DB_HOST,
    "port": config.Config.DB_PORT,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}


# Constants for Fee Calculation
PARTNERSHIP_FEE_CONDITIONS = [
    (5952.38, 20, 1),  # First-line children → Parent gets 10%
    (29761.90, 20, 2),  # Second-line children → Parent gets 10%
    (59523.81, 10, 3),  # Third-line children → Parent gets 5%
    (119047.62, 10, 4)  # Fourth-line children → Parent gets 5%
]


# Load Account Balances from JSON
def load_account_balances(file_path):
    with open(file_path, "r") as file:
        accounts_data = json.load(file)

    return {int(acc["accountId"]): float(acc["statement"]["availableBalance"]) for acc in accounts_data}

# Load accounts.json for eWallet lookup
def load_accounts_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Fetch organization structure using Recursive CTE
def fetch_org_structure(my_id):
    conn = mysql.connector.connect(**db_config)
    query = """
    WITH RECURSIVE child_accounts AS (
        SELECT id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID
        FROM pamm_master WHERE pid = %s
        UNION ALL
        SELECT a.id, a.pid, a.accountNumber, a.clientID, a.name, a.email, a.nickname, a.parentAccountNumber, a.parentClientID
        FROM pamm_master a INNER JOIN child_accounts ca ON a.pid = ca.id
    )
    SELECT * FROM child_accounts;
    """
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (my_id,))
            data = cursor.fetchall()
    finally:
        conn.close()
    return data

# Find eWallet account for given clientID
def find_ewallet_account(client_id, accounts_data):
    for account in accounts_data:
        if (
            account["clientId"] == client_id
            and account["platform"]["caption"] == "eWallet"
            and account["platform"]["id"] == 1
            and account["group"]["id"] == 3
            and account["group"]["name"] == "Fiat"
        ):
            return {
                "accountId": account["accountId"],
                "accountNumber": account["accountNumber"],
            }
    return None

# Process hierarchy and apply fee calculation
def process_hierarchy_with_ewallet(org_structure, account_balances, root_id, accounts_data):
    hierarchy = {}

    for account in org_structure:
        account_id = int(account["id"])
        parent_id = account["pid"]

        if account_id not in hierarchy:
            hierarchy[account_id] = {
                "details": account,
                "balance": account_balances.get(account_id, 0),
                "children": [],
                "receivingFromAccounts": [],
                "givingToAccounts": []
            }

        if parent_id:
            parent_id = int(parent_id)
            if parent_id not in hierarchy:
                hierarchy[parent_id] = {
                    "details": {},
                    "balance": account_balances.get(parent_id, 0),
                    "children": [],
                    "receivingFromAccounts": [],
                    "givingToAccounts": []
                }
            hierarchy[parent_id]["children"].append(account_id)

    for parent_id, parent_data in hierarchy.items():
        total_first_line_balance = sum(hierarchy[child]["balance"] for child in parent_data["children"])

        for threshold, percentage, level in PARTNERSHIP_FEE_CONDITIONS:
            if total_first_line_balance >= threshold:
                for child_id in get_nth_line_children(hierarchy, parent_id, level):
                    parent_data["receivingFromAccounts"].append({"accountId": child_id, "percentage": f"{percentage}%"})
                    if parent_id != root_id:
                        client_id = hierarchy[parent_id]["details"].get("clientID")
                        ewallet_account = find_ewallet_account(client_id, accounts_data)
                        if ewallet_account:
                            hierarchy[child_id]["givingToAccounts"].append({
                                "accountId": ewallet_account["accountId"],
                                "accountNumber": ewallet_account["accountNumber"],
                                "percentage": f"{percentage}%"
                            })

    return hierarchy

# Helper function to get nth-line children
def get_nth_line_children(hierarchy, parent_id, depth):
    current_level = set(hierarchy[parent_id]["children"])
    for _ in range(depth - 1):
        next_level = set()
        for acc_id in current_level:
            next_level.update(hierarchy[acc_id]["children"])
        current_level = next_level
    return current_level

# Generate final JSON output
def generate_json_output(hierarchy):
    result = []
    for account_id, data in hierarchy.items():
        result.append({
            "accountId": account_id,
            "balance": data["balance"],
            "receivingFromAccounts": data["receivingFromAccounts"],
            "givingToAccounts": data["givingToAccounts"],
            **data["details"]
        })
    return json.dumps(result, indent=4)

# Main Execution
if __name__ == "__main__":
    root_id = 1030
    account_balances = load_account_balances("../daily_files/accounts_data.json")
    accounts_data = load_accounts_data("../daily_files/accounts_data.json")
    org_structure = fetch_org_structure(root_id)
    processed_hierarchy = process_hierarchy_with_ewallet(org_structure, account_balances, root_id, accounts_data)
    final_json = generate_json_output(processed_hierarchy)

    with open("final_hierarchy_analysis.json", "w") as outfile:
        outfile.write(final_json)

    print("✅ Analysis completed with eWallet accounts. JSON saved as 'final_hierarchy_analysis.json'.")
