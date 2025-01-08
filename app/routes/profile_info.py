from flask import Blueprint, render_template
from app.models.profile import Profile
from app.utils.middleware import token_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session as flask_session, jsonify
from datetime import timedelta
import requests
import requests.sessions
import json

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/profile-info')
@token_required
def get_profile_info():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()

    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    return render_template('profile/profile_info.html', profile_data=profile_data)


@profile_bp.route('/update-nick-name', methods=["POST"])
@token_required
def update_nick_name():
    data = request.json
    new_nickname = data.get("nickname")
    client_id = data.get("clientid")

    update_nick_name = Profile.update_nick_name(client_id=client_id, newNickName=new_nickname)
    if update_nick_name == 200:
        profile_data = Profile.fetch_profile_info()
        return render_template('profile/profile_info.html', profile_data=profile_data)
    else:
        return render_template('error.html')

@profile_bp.route('/verification')
@token_required
def get_verification_info():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()

    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    return render_template('profile/verification.html', profile_data=profile_data)

@profile_bp.route('/upload-documents')
@token_required
def upload_documents():
    """Fetch profile info and render the dashboard page."""
    profile_data = Profile.fetch_profile_info()

    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    return render_template('profile/upload-documents.html', profile_data=profile_data)
