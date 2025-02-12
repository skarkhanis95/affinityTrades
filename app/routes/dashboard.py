import json

from flask import Blueprint, render_template
from app.models.profile import Profile
from app.utils.middleware import token_required
from app.models.wallets import Wallets
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@token_required
def dashboard():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()

    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    wallets_data = Wallets.fetch_wallets_info()
    #print(json.dumps(wallets_data))
    if not wallets_data:
        return render_template('error.html', message="Failed to load profile data")

    transactions_data = Wallets.fetch_transactions()
    #print(json.dumps(transactions_data))
    if not transactions_data:
        return {}

    return render_template('dashboard/dashboard.html', wallets_data=wallets_data, profile_data=profile_data,
                           transactions_data=transactions_data)
