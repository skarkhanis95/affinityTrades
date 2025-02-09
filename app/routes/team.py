from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.models.org import Organization
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
import config
import mysql.connector

team_bp = Blueprint('team', __name__, url_prefix='/team')


db_config = {
    "host": config.Config.DB_HOST,
    "port": config.Config.DB_PORT,
    "user": config.Config.DB_USER,
    "password": config.Config.DB_PASSWORD,
    "database": config.Config.DATABASE,
}



@team_bp.route('/')
@token_required
def select_pamm_account():
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    wallets_data = Wallets.fetch_wallets_info()
    if not wallets_data:
        return render_template('error.html', message="Failed to load wallets data")

    pamm_accounts = []
    for wallet in wallets_data["data"]:
        if wallet.get("group", {}).get("id") == 16 and wallet.get("platform", {}).get("isDemo") is False:
            pamm_accounts.append(wallet)

    # pass blank data
    team_data = []

    return render_template('team/team.html',  profile_data=profile_data, org_data=team_data, pamm_accounts=pamm_accounts)

@team_bp.route('/team-chart', methods=["GET"])
@token_required
def get_team_info():
    accountData = request.args.get('accountData')
    accountID = accountData.split(',')[0]
    accountNumber = accountData.split(',')[1]

    team_data = Organization.get_org_tree_info(master_account_number=accountNumber, master_account_id=accountID)

    if team_data:
        level = team_data[0].get("level", "No Level")
        print(f"Level: {level}")

        return jsonify({"success": True, "teamData": team_data, "level": level})
    else:
        return jsonify({"success": False, "message": "Your Account is Not Configured for Team Org Structure. Please contact Helpdesk"})
    # profile_data = Profile.fetch_profile_info()
    # if not profile_data:
    #     return render_template('error.html', message="Failed to load profile data")
    #
    # wallets_data = Wallets.fetch_wallets_info()
    # if not wallets_data:
    #     return render_template('error.html', message="Failed to load wallets data")
    #
    #
    # team_data = Organization.get_org_tree_info(10590,1032)
    # print(team_data)
    #
    #
    # return render_template('team/team.html',  profile_data=profile_data, org_data=team_data)

@team_bp.route('/referral')
@token_required
def select_referral_pamm_account():
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    wallets_data = Wallets.fetch_wallets_info()
    if not wallets_data:
        return render_template('error.html', message="Failed to load wallets data")

    pamm_accounts = []
    for wallet in wallets_data["data"]:
        if wallet.get("group", {}).get("id") == 16 and wallet.get("platform", {}).get("isDemo") is False:
            pamm_accounts.append(wallet)

    validated_accounts = Organization.validate_accounts_in_referral(pamm_accounts)
    if not validated_accounts:
        validated_accounts = []

    # pass blank data
    team_data = []

    return render_template('team/referral.html',  profile_data=profile_data, org_data=team_data, pamm_accounts=validated_accounts)

@team_bp.route('/referral-data', methods=["GET"])
@token_required
def get_ref_info():
    accountData = request.args.get('accountData')
    accountID = accountData.split(',')[0]
    accountNumber = accountData.split(',')[1]

    ref_data = Organization.get_referral_data(accountID)

    if ref_data:
        return jsonify({"success": True, "data": ref_data})
    else:
        return jsonify({"success": False, "message": "Your Account is Not Configured for Team Org Structure. Please contact Helpdesk"})

@team_bp.route('/generate-refId', methods=["POST"])
@token_required
def generate_referral_id():
    """
    API to generate a random referral ID and update it in the database.
    """
    data = request.json
    account_id = data.get("accountId")
    ref_id = data.get("accountId")

    if not account_id or not ref_id:
        return jsonify({"success": False, "message": "accountId and refId are required"}), 400

    conn = mysql.connector.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            query = "UPDATE pamm_master SET refId = %s WHERE id = %s"
            cursor.execute(query, (ref_id, account_id))
            conn.commit()

        return jsonify({"success": True, "message": "Referral ID updated successfully", "refId": ref_id})
    finally:
        conn.close()
