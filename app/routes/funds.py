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


@funds_bp.route('/withdrawal')
@token_required
def withdrawal():
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")


    withdrawal_data = Funds.get_withdrawl_info()
    if not withdrawal_data:
        return render_template('error.html', message="Failed to load transfer data")

    return render_template('funds/withdrawal.html', profile_data=profile_data,
                           withdrawal_data=withdrawal_data)


@funds_bp.route('/get-withdrawal-form', methods=["GET"])
@token_required
def get_withdrawal_form():
    fromAccountId = int(request.args.get('fromAccountId'))
    currency = int(request.args.get('currency'))
    deviceTimezone = request.args.get('deviceTimezone')
    paymentMethod = request.args.get('paymentMethod')

    # Create the payload to send to the external API
    payload = {
        "accountId": fromAccountId,
        "currencyCode": currency,
        "deviceTimezone": deviceTimezone,
        "locale": "en"
    }

    withdrawal_uri = f"{config.Config.API_BASE_URL}/withdrawal-methods/{paymentMethod}/form"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = make_authenticated_request("POST", url=withdrawal_uri, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            id = data.get("id")
            if id:
                return jsonify({"success": True, "id": id})
            else:
                print(response.status_code)
                print(response.text)
                print(response.content)
                return jsonify({"success": False, "message": "Could Not Get Form ID from External API"})
        else:
            return jsonify({"success": False, "message": "Error with the external API"})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


@funds_bp.route('/get-withdrawal-preview', methods=["GET"])
@token_required
def get_withdrawal_preview():
    amount = request.args.get("amount")
    fromAccountId = int(request.args.get('fromAccountId'))
    currency = int(request.args.get('currency'))
    paymentMethod = int(request.args.get('paymentMethod'))

    # Create the payload to send to the external API
    payload = {
        "amount": amount,
        "accountId": fromAccountId,
        "currencyCode": currency,
        "methodId": paymentMethod,
    }

    withdrawal_uri = f"{config.Config.API_BASE_URL}/withdrawals/preview"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = make_authenticated_request("POST", url=withdrawal_uri, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rate = data.get("rate")
            dataAmount = data.get("amount")
            commission = data.get("commission")
            sourceCurrencyAlphaCode = data.get("sourceCurrencyAlphaCode")
            sourceCurrencyAmount = data.get("sourceCurrencyAmount")
            destinationCurrencyAlphaCode = data.get("destinationCurrencyAlphaCode")
            destinationCurrencyAmount = data.get("destinationCurrencyAmount")
            if rate and dataAmount and commission and sourceCurrencyAlphaCode and sourceCurrencyAmount and destinationCurrencyAmount and destinationCurrencyAlphaCode:
                return jsonify({
                    "success": True,
                    "rate": rate,
                    "amount": dataAmount,
                    "commission": commission,
                    "sourceCurrencyAlphaCode": sourceCurrencyAlphaCode,
                    "sourceCurrencyAmount": sourceCurrencyAmount,
                    "destinationCurrencyAlphaCode": destinationCurrencyAlphaCode,
                    "destinationCurrencyAmount": destinationCurrencyAmount
                })
            else:
                print(response.status_code)
                print(response.text)
                print(response.content)
                return jsonify({"success": False, "message": "Could Not Get Form ID from External API"})
        else:
            return jsonify({"success": False, "message": "Error with the external API"})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


@funds_bp.route('/confirm-withdrawal', methods=["POST"])
@token_required
def confirm_withdrawal():
    data = request.get_json()
    id = str(data["id"])
    methodId = int(data["methodId"])
    accountId = int(data["accountId"])
    currencyCode = int(data["currencyCode"])
    amount = str(data["amount"])
    additionalData = {
        "9f34ddb9-421f-4ecb-8c56-77bfde1c1da5": data["accountHolderName"],
        "af1f5a3e-c04d-44a8-96d6-103f4058d6be": data["bankName"],
        "3c8929d1-7bb2-45a6-9f38-d349fb36f8d4": data["accountNumber"],
        "db5eb57e-3010-43cd-a6d1-2f158b8c392c": data["bankIFSCCode"]
    }

    # Create the payload to send to the external API
    payload = {
        "id": id,
        "methodId": methodId,
        "accountId": accountId,
        "currencyCode": currencyCode,
        "amount": amount,
        "data": additionalData

    }

    withdrawal_uri = f"{config.Config.API_BASE_URL}/withdrawals"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = make_authenticated_request("POST", url=withdrawal_uri, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            id = data.get("id")
            confirmationChannel = data.get("confirmationChannel")
            if id and confirmationChannel:
                return jsonify({
                    "success": True,
                    "id": id,
                    "confirmationChannel": confirmationChannel
                })
            else:
                print(response.status_code)
                print(response.text)
                print(response.content)
                return jsonify({"success": False, "message": "Could Not Get Verification Channel From External API"})
        else:
            return jsonify({"success": False, "message": "Error with the external API"})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


@funds_bp.route('/validate-withdrawal', methods=["GET"])
@token_required
def validate_withdrawal():
    id = request.args.get("formId")
    code = request.args.get('code')



    # Create the payload to send to the external API
    payload = {
        "id": id,
        "code": code
    }


    withdrawal_uri = f"{config.Config.API_BASE_URL}/withdrawals/confirm"
    headers = {
        "accept-language": "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        response = make_authenticated_request("POST", url=withdrawal_uri, json=payload, headers=headers)
        if response.status_code == 204:
            return jsonify({"success": True}), 204
        else:
            print(response.status_code)
            print(response.text)
            print(response.content)
            return jsonify({"success": False, "message": f"Could Not Validate Your Request: {response.text}"})

    except requests.exceptions.RequestException as e:
        print("Inside Execption")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})