import requests
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import pandas as pd

# MySQL connection setup
# Read the CSV file into pandas DataFrame
df = pd.read_csv('sample_master.csv')
df = df.where(pd.notnull(df), None)

# Establish MySQL connection
db_connection = mysql.connector.connect(
    host="localhost",         # e.g., "localhost"
    user="affinity_db_user",     # e.g., "root"
    password="whisky3115", # e.g., "password"
    database="affinityTrades"  # e.g., "test_db"
)

# Create cursor object to interact with MySQL
cursor = db_connection.cursor()

# Insert data from DataFrame to MySQL table
for index, row in df.iterrows():
    # Create the SQL query to insert data
    sql = """
    INSERT INTO pamm_master (id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        row['id'], row['pid'], row['accountNumber'], row['clientID'],
        row['name'], row['email'], row['nickname'],
        row['parentAccountNumber'], row['parentClientID']
    )

    # Execute the query with the values from each row
    cursor.execute(sql, values)

# Commit the transaction to save changes
db_connection.commit()

# Close the cursor and connection
cursor.close()
db_connection.close()

print("CSV data uploaded successfully!")