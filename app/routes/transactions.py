from flask import Blueprint, render_template
from app.models.profile import Profile
from app.models.wallets import Wallets
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from datetime import timedelta
import requests
import requests.sessions
import json
import os
import config
import pandas as pd
from io import StringIO
from flask import Response

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions_bp.route('/')
@token_required
def transactions():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()
    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")


    wallets_data = Wallets.fetch_wallets_info()
    if not wallets_data:
        return render_template('error.html', message="Failed to load profile data")

    transactions_data = Wallets.fetch_transactions()
    if not transactions_data:
        return {}

    return render_template('transactions/transactions-history.html', wallets_data=wallets_data, profile_data=profile_data,
                           transactions_data=transactions_data)

@transactions_bp.route('/export-transactions')
@token_required
def export_transactions():
    """Fetch profile info and render the dashboard page."""

    transactions_data = Wallets.fetch_transactions()
    if not transactions_data:
        return {}

    transactions_data_export = transactions_data["data"]

    # Convert the transaction data into a Pandas DataFrame
    df = pd.DataFrame(transactions_data_export)

    # Create an in-memory buffer
    output = StringIO()
    df.to_csv(output, index=False)  # Convert DataFrame to CSV (no index column)
    output.seek(0)  # Move to the start of the buffer

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )