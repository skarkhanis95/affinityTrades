from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.models.funds import Funds
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from app.utils.api_helpers import make_authenticated_request
from datetime import timedelta
import requests
import requests.sessions
import json
import os
import config

funds_bp = Blueprint('funds', __name__, url_prefix='/funds')

@funds_bp.route('/deposit')
@token_required
def deposit():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")


    wallets_data = Wallets.fetch_wallets_info()
    if not wallets_data:
        return render_template('error.html', message="Failed to load wallets data")

    transactions_data = Wallets.fetch_transactions()

    if not transactions_data:
        return {}
    deposit_transactions = [transaction for transaction in transactions_data["data"] if
                            transaction["type"] == "deposit"]

    deposit_data = Funds.get_deposit_info()


    return render_template('funds/deposit.html', wallets_data=wallets_data, profile_data=profile_data,
                           transactions_data=deposit_transactions, deposit_data=deposit_data)


@funds_bp.route('/submit-deposit', methods=['POST'])
@token_required
def submit_deposit():
    account_id = request.form.get('accountNumber')
    currency = request.form.get('currency')
    payment_method = request.form.get('paymentMethod')
    to_pay_amount = request.form.get('toPayAmount')
    to_get_amount = request.form.get('toGetAmount')
    transfer_amount = request.form.get('transferAmount')
    mobile_number = request.form.get('mobileNumber')

    # Log the data or process it

    payload = {
        "methodId": int(payment_method),
        "accountId": int(account_id),
        "currencyCode": int(currency),
        "amount": int(transfer_amount),
        "data":{"account": int(transfer_amount), config.Config.INR_DEPOSIT_DATA_MOBILE_FIELD: int(mobile_number)}
    }

    headers = {
        'Content-Type': 'application/json'
    }
    url = config.Config.POST_DEPOSIT_API
    response = make_authenticated_request("POST", url=url, headers=headers, json=payload)
    if response.status_code != 201:
        return render_template('error.html', message="Failed to load profile data")
    print(response.text)
    return redirect('/funds/deposit')


@funds_bp.route('/transfer')
@token_required
def transfer():
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")


    transfer_data = Funds.get_transfer_info()
    if not transfer_data:
        return render_template('error.html', message="Failed to load transfer data")

    return render_template('funds/transfer.html', profile_data=profile_data,
                           transfer_data=transfer_data)

@funds_bp.route('/check-transfer', methods=["GET"])
@token_required
def check_transfer():
    from_account = int(request.args.get('fromAccount'))
    to_account = int(request.args.get('toAccount'))
    amount = float(request.args.get('amount'))

    # Create the payload to send to the external API
    payload = {
        "source_id": from_account,
        "destination_id": to_account,
        "amount": amount
    }
    headers = {}
    try:
        url = config.Config.CAN_TRANSFER_API
        headers = {
            'Content-Type': 'application/json'
        }
        response = make_authenticated_request("POST", url=url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()["data"]
            if data.get("can_transfer") is True:
                return jsonify({"success": True})
            else:
                print(response.status_code)
                print(response.text)
                print(response.content)
                return jsonify({"success": False, "message": data.get("message", "Invalid transfer")})
        else:
            return jsonify({"success": False, "message": "Error with the external API"})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})



    #return render_template('funds/transfer.html', profile_data=profile_data)


@funds_bp.route('/confirm-transfer', methods=["POST"])
@token_required
def confirm_transfer():
    #{amount: "1", calc: 1, destination_id: 1307, source_id: 1306, pretend: false}
    data = request.get_json()
    amount = str(data["amount"])
    calc = float(data["amount"])
    source_id = int(data["fromAccount"])
    destination_id = int(data["toAccount"])
    pretend = False

    payload = {
        "amount": amount,
        "calc": calc,
        "source_id": source_id,
        "destination_id": destination_id,
        "pretend": False
    }
    try:
        url = config.Config.TRANSFER_API
        headers = {
            'Content-Type': 'application/json'
        }
        response = make_authenticated_request("POST", url=url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 201:
                return jsonify({"success": True, "message": "Transfer confirmed successfully"})
            else:
                print(response.status_code)
                print(response.text)
                print(response.content)
                return jsonify({"success": False, "message": "Transfer failed to confirm"})
        else:
            return jsonify({"success": False, "message": "Error with the external API"})
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


