from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.models.funds import Funds
from app.models.org import Organization
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from app.utils.api_helpers import make_authenticated_request
from datetime import timedelta
import requests
import requests.sessions
import json
import os
import config

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/')
@token_required
def get_team_info():
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    wallets_data = Wallets.fetch_wallets_info()
    if not wallets_data:
        return render_template('error.html', message="Failed to load wallets data")


    team_data = Organization.get_org_tree_info(10590,1032)
    print(team_data)


    return render_template('team/team.html',  profile_data=profile_data, org_data=team_data)