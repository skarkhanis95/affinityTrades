import requests
from app.services.auth_service import AuthService


def make_authenticated_request(method, url, **kwargs):
    """Makes an API request with a valid access token."""
    # Get a valid access token
    token = AuthService.get_access_token()
    if not token:
        raise Exception("User not authenticated or token expired.")

    # Ensure headers are not modified in place
    headers = kwargs.pop("headers", {})  # Copy headers if provided
    headers = {**headers, "Authorization": f"Bearer {token}"}  # Merge with Authorization

    # Pass the updated headers back into kwargs
    kwargs["headers"] = headers

    # Make the API request
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response


