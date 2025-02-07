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
from app.models.register import Register

register_bp = Blueprint('register', __name__, url_prefix='/register')

@register_bp.route('/')
def register():
    ref_id = request.args.get("refId")  # returns None if ?ref=... is not in the URL

    # Do something with ref_id (or ignore if it's None)
    if ref_id:
        # e.g., track the referral, store in a database, etc.
        ref_data = {"refID": ref_id}
    else:
        ref_data = {"refID": None}


    return render_template('register.html', ref_data=ref_data)

@register_bp.route('/client', methods=['POST'])
def register_new_client():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get("RePassword")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        birthDate = request.form.get("birthDate")
        countryCode = request.form.get("countryCode")
        mobileNumber = request.form.get("mobileNumber")
        fullMobileNumber = f"{countryCode}{mobileNumber}"
        refId = request.form.get("refId")
        chckAdult = request.form.get("chckAdult")
        chckCountries = request.form.get("chckCountries")
        device_fingerprint = request.form.get('device_fingerprint')


        # Get the Wizard UUID
        wizard_payload = {
            "utm": {
                "utm_uri": "https://my.affinitytrades.com/en/auth/sign-up",
                "utm_referrer": "https://affinitytrades.com/"
            }
        }
        signup_wizard_url = "https://api.affinitytrades.com/api/v2/my/signup/wizard"
        wizard_headers = {
            "Content-Type": "application/json"
        }
        wizard_response = requests.post(url=signup_wizard_url, headers=wizard_headers, json=wizard_payload)
        if wizard_response.status_code != 200:
            print(f"Wizard Status Code: {wizard_response.status_code}")
            print(f"Wizard Response Text: {wizard_response.text}")
            return render_template('error.html', message="Failed to get Sign Up Wizard Response")
        wizard_data = wizard_response.json()
        signup_uuid = wizard_data["uuid"]
        print(f"UUID: {signup_uuid}")

        if signup_uuid is not None or signup_uuid == "":
            signup_payload = {
                "email": email,
                "password": password,
                "password_confirmation": repassword,
                "info": {
                    "givenName": firstName,
                    "familyName": lastName,
                    "birthday": birthDate,
                },
                "phones":{
                    "0": {
                        "phone": fullMobileNumber
                    }
                },
                "requirements": {
                    "adult": True,
                    "resident": True
                },
                "uuid": signup_uuid,
                "device_fingerprint": device_fingerprint
            }

            print(f"Signup Payload: {json.dumps(signup_payload)}")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            signup_url = "https://api.affinitytrades.com/api/v2/my/signup"
            response = requests.post(url=signup_url, headers=headers, json=signup_payload)
            if response.status_code != 200:
                print(f"Signup COde: {response.status_code}")
                print(f"Signup Response Text: {response.text}")
                print(f"Signup Response Content: {response.content}")
                return render_template('error.html', message="Failed to register new client")
            data = response.json()
            if data.get("code") == 202:
                print(data.get("code"))
                accessToken = data.get("data", {}).get("accessToken", {}).get("token", "")
                refreshToken = data.get("data", {}).get("refreshToken", {}).get("token", "")
                print(f"Access Toeken: {accessToken}")
                print(f"Refresh Toeken: {refreshToken}")
                if refId is not None and refId != "":
                    print("going in with refId")
                    register = Register.create_pamm_account(
                        accessToken=accessToken,
                        refreshToken=refreshToken,
                        refId=refId
                    )
                else:
                    print("going in WITHOUT refId")
                    register = Register.create_pamm_account(
                        accessToken=accessToken,
                        refreshToken=refreshToken
                    )

                if register:
                    return redirect("/auth/login", code=200)


    return None
