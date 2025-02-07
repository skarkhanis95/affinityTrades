from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.models.funds import Funds
from app.models.pamm import PAMM
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from app.utils.api_helpers import make_authenticated_request
from datetime import timedelta
import requests
import requests.sessions
import json
import os
import config

pamm_bp = Blueprint('pamm', __name__, url_prefix='/pamm')

@pamm_bp.route('/accounts')
@token_required
def get_pamm_accounts():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    pamm_data = PAMM.get_accounts_info()
    if not pamm_data:
        return render_template('error.html', message="Failed to load profile data")


    return render_template('pamm/accounts.html', profile_data=profile_data, pamm_data=pamm_data)
