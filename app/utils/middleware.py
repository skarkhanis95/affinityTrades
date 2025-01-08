from functools import wraps
from flask import session, redirect, url_for
from app.services.auth_service import AuthService


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = AuthService.get_access_token()
        if not access_token:
            # Clear session and redirect to login if tokens are invalid
            session.clear()
            return redirect(url_for("auth.login"))

        # Pass the token to the wrapped function if needed
        return f(*args, **kwargs)

    return decorated_function