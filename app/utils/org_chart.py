import requests
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import pandas as pd
import config
from app.services.service_account_manager import ServiceAccountManager
from app.utils.logger import logger

sm = ServiceAccountManager()
db_config = {
    "host": config.Config.DB_HOST,
    "port": config.Config.DB_PORT,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}

def get_child_accounts(myid):

    try:
        logger.info("Trying to Get Child Accounts")
        # Connect to the MySQL database
        db_connection = mysql.connector.connect(
            host=config.Config.DB_HOST,  # e.g., "localhost"
            user=config.Config.DB_USER,
            port=config.Config.DB_PORT,
            password=config.Config.DB_PASSWORD,  # e.g., "password"
            database=config.Config.DATABASE  # e.g., "test_db"
        )


        # Create a cursor object
        cursor = db_connection.cursor()

        # Define the recursive query with a placeholder for the pid (myid)
        query = """
        WITH RECURSIVE child_accounts AS (
            -- Base case: Select the first level children where pid = myid
            SELECT id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID
            FROM pamm_master
            WHERE pid = %s  -- Placeholder for myid
    
            UNION ALL
    
            -- Recursive case: Get child accounts of the previous level
            SELECT a.id, a.pid, a.accountNumber, a.clientID, a.name, a.email, a.nickname, a.parentAccountNumber, a.parentClientID
            FROM pamm_master a
            INNER JOIN child_accounts ca ON a.pid = ca.id
        )
        -- Final selection: Get all child accounts (including sub-children and so on)
        SELECT * FROM child_accounts;
        """

        # Execute the query, passing myid as a parameter
        cursor.execute(query, (myid,))

        # Fetch all results
        results = cursor.fetchall()
        columns = ['accountId', 'pid', 'accountNumber', 'clientID', 'name', 'email', 'nickname', 'parentAccountNumber',
                   'parentClientID']
        results_dict = [dict(zip(columns, row)) for row in results]
        # Close the cursor and connection
        cursor.close()
        db_connection.close()
        logger.info("Database accessed adn records fetched")
        return results_dict
    except Exception as e:
        logger.error(f"Error in getting Child Accounts from Database: {e}")
        return None


def get_master_account(account_number):
    try:
        # Connect to the MySQL database
        db_connection = mysql.connector.connect(
            host=config.Config.DB_HOST,  # e.g., "localhost"
            user=config.Config.DB_USER,
            port=config.Config.DB_PORT,
            password=config.Config.DB_PASSWORD,  # e.g., "password"
            database=config.Config.DATABASE  # e.g., "test_db"
        )


        # Create a cursor object
        cursor = db_connection.cursor()


        # Define the query to get the parent account based on account number
        query = """
            SELECT id, pid, accountNumber, clientID, name, email, nickname,
            parentAccountNumber, parentClientID
            FROM pamm_master 
            WHERE accountNumber = %s
            """

        # Execute the query, passing the account_number as a parameter
        cursor.execute(query, (account_number,))

        # Fetch the result
        results = cursor.fetchall()

        columns = ['accountId', 'pid', 'accountNumber', 'clientID', 'name', 'email', 'nickname', 'parentAccountNumber',
                   'parentClientID']

        # Convert the results into a list of dictionaries
        results_dict = [dict(zip(columns, row)) for row in results]
        for row in results_dict:
            if 'pid' in row:
                del row['pid']


        # Close the cursor and connection
        cursor.close()
        db_connection.close()

        return results_dict

    except Exception as e:
        print(f"Error in fetching paamm accounts from database server: {e}")
        return None


