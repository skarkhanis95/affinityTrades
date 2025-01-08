from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from datetime import timedelta
import requests
import requests.sessions
import json
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# @auth_bp.before_request
# def check_session_expiry():
#     if 'access_token' not in flask_session:
#         flash("Your session has expired. Please log in again.", "warning")
#         return redirect(url_for('auth.login'))


@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        """Login route that uses AuthService to authenticate."""
        email = request.form.get('email')
        password = request.form.get('password')
        device_fingerprint = request.form.get('device_fingerprint')

        if AuthService.login(email, password, device_fingerprint):
            return redirect(url_for('dashboard.dashboard'))  # Redirect to dashboard after login
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Logout route that clears the session."""
    flask_session.clear()
    return redirect(url_for("auth.login"))