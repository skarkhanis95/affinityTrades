import time
from app.services.auth_service import AuthService
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from app.utils.logger import logger

class ServiceAccountManager:
    def __init__(self):
        self.email = config.Config.SERVICE_ACCOUNT_EMAIL  # Retrieve from config
        self.password = config.Config.SERVICE_ACCOUNT_PASSWORD  # Retrieve from config
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def login(self):
        """Authenticate the service account and retrieve tokens."""
        try:
            signin_url = config.Config.ADMIN_SIGNIN_URL
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
            payload = {"email": self.email, "password": self.password}
            response = requests.post(url=signin_url, headers=headers, json=payload)
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["accessToken"]["token"]
                self.refresh_token = tokens["refreshToken"]["token"]
                self.token_expiry = time.time() + 10 * 60  # 10 minutes from now
                logger.debug("Service account successfully logged in.")
            else:
                logger.error("Login to Service Account Failed")
                raise
        except Exception as e:
            logger.error(f"Login to Service Account Failed. Error: {e}")
            raise

    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        try:
            refresh_url = config.Config.ADMIN_REFRESH_URL
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0',
                'Authorization': f'Bearer {self.access_token}'
            }
            payload = {"refreshToken": self.refresh_token}
            response = requests.post(url=refresh_url, headers=headers, json=payload)
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["accessToken"]["token"]
                self.refresh_token = tokens["refreshToken"]["token"]
                self.token_expiry = time.time() + 10 * 60  # Reset expiration
                logger.debug("Access token successfully refreshed.")
            else:
                logger.error("Login to Service Account Failed")
                raise
        except Exception as e:
            logger.error(f"Token Refresh Failed: {e}")
            # Fall back to a fresh login if refresh fails
            self.login()

    def get_valid_access_token(self):
        """Ensure a valid access token is available."""
        if not self.access_token or time.time() >= self.token_expiry - 30:  # Renew 30 seconds before expiry
            if not self.refresh_token or time.time() >= self.token_expiry:  # If refresh token also expired
                logger.debug("Both tokens expired. Logging in again.")
                self.login()
            else:
                logger.debug("Access token expired. Refreshing token.")
                self.refresh_access_token()
        return self.access_token

    def make_api_call(self, method, url, **kwargs):
        """Make an authenticated API call using the service account."""
        token = self.get_valid_access_token()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        return requests.request(method, url, **kwargs)
