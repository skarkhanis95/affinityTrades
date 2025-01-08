import base64
from app.utils.api_helpers import make_authenticated_request
import config
import requests
from flask import session as flask_session


class Profile:
    @staticmethod
    def fetch_profile_info():
        """Fetch user profile information and handle photo processing."""

        if not flask_session.get("profileInfo"):

            try:
                url = config.Config.PROFILE_ENDPOINT
                # Make an API call to fetch profile data
                response = make_authenticated_request("GET", url)
                response.raise_for_status()
                profile_data = response.json().get('data')

                # Extract first and last names
                first_name = profile_data["info"].get("givenName", "User")
                last_name = profile_data["info"].get("familyName", "Unknown")

                # Handle the photo attribute
                initials = f"{first_name[:1].upper()}{last_name[:1].upper()}"
                profile_data["initials"] = initials
                # if not profile_data.get("photo"):
                #     # Generate initials if no photo
                #
                #     profile_data["photo_url"] = None
                #
                # else:
                #     # Fetch the profile photo if it exists
                #     photo_url = config.Config.PROFILE_PHOTO_API
                #     photo_response = make_authenticated_request("GET", photo_url)
                #     photo_response.raise_for_status()
                #
                #     # Convert the image to Base64 format
                #     image_base64 = base64.b64encode(photo_response.content).decode('utf-8')
                #     profile_data["photo_url"] = f"data:image/png;base64,{image_base64}"
                flask_session["profileInfo"] = profile_data
                return profile_data
            except requests.exceptions.RequestException as e:
                print(f"Error fetching profile data: {e}")
                return None

        else:
            profile_data = flask_session.get("profileInfo")
            return profile_data


    def update_nick_name(client_id, newNickName):
        url = f"https://api.affinitytrades.com/api/v1/client/{client_id}"
        payload = {
            "nickname": newNickName
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = make_authenticated_request("POST", url, headers=headers, json=payload)
            if response.status_code != 200:
                return response.status_code
            else:
                if "profileInfo" in flask_session:
                    profile_data = flask_session["profileInfo"]
                    profile_data["nickname"] = newNickName
                    # update session info
                    flask_session["profileInfo"] = profile_data
                return 200
        except requests.exceptions.RequestException as e:
            print(f"Error in updating NickName: {e}")
        return None

    @staticmethod
    def fetch_documents_info():
        # TODO
        pass
