from flask import Blueprint, render_template
from app.models.profile import Profile
from app.utils.middleware import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@token_required
def dashboard():
    """Fetch profile info and render the dashboard page."""
    print("Authenticated")
    profile_data = Profile.fetch_profile_info()

    if not profile_data:
        return render_template('error.html', message="Failed to load profile data")

    print(profile_data["email"])  # Debug log
    return render_template('dashboard/dashboard.html', profile_data=profile_data)