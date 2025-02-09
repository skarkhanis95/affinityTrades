from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.models.funds import Funds
from app.utils.middleware import token_required, manager_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from app.utils.api_helpers import make_authenticated_request
from datetime import timedelta
import requests
import requests.sessions
import json
import os
import config
import mysql.connector

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')



db_config = {
    "host": config.Config.DB_HOST,
    "port": config.Config.DB_PORT,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}

@manager_bp.route('/relationship')
@token_required
@manager_required
def manager_home():

    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    return render_template('manager/relationship.html', profile_data=profile_data)


@manager_bp.route('/data')
@token_required
@manager_required
def get_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch all necessary fields
    cursor.execute("""
        SELECT id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID, refId FROM pamm_master
    """)
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({"data": data})


# Update Data in MySQL
@manager_bp.route('/update', methods=['POST'])
@token_required
@manager_required
def update_data():
    req_data = request.json
    column = req_data.get('column')
    value = req_data.get('value')
    row_id = req_data.get('id')

    # Prevent SQL Injection by ensuring only allowed columns are updated
    allowed_columns = ["pid", "accountNumber", "clientID", "name", "email", "nickname", "parentAccountNumber",
                       "parentClientID", "refId"]
    if column not in allowed_columns:
        return jsonify({"error": "Invalid column"}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Update only the specified column
    query = f"UPDATE pamm_master SET {column} = %s WHERE id = %s"
    cursor.execute(query, (value, row_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})

@manager_bp.route('/add', methods=['POST'])
@token_required
@manager_required
def add_record():
    req_data = request.json
    id = req_data.get('id')
    pid = req_data.get('pid')
    accountNumber = req_data.get('accountNumber')
    clientID = req_data.get('clientID')
    name = req_data.get('name')
    email = req_data.get('email')
    nickname = req_data.get('nickname')
    parentAccountNumber = req_data.get('parentAccountNumber')
    parentClientID = req_data.get('parentClientID')
    refId = req_data.get('refId')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    INSERT INTO pamm_master (id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID, refId)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (id, pid, accountNumber, clientID, name, email, nickname, parentAccountNumber, parentClientID, refId))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})

