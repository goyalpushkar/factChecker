# Import necessary libraries
import logging
from readProperties import PropertiesReader
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import Flow
from flask import json, jsonify, session
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Authorization:
    def __init__(self):
        self.properties = PropertiesReader("config.properties")
        # Allow insecure transport for local development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    def __str__(self):
        return f"{Authorization.__name__}"

    def get_session_credentials(self):
        """
        Retrieves OAuth 2.0 credentials from the session.
        """
        credentials_data = session.get("credentials")
        if not credentials_data:
            logging.error("No credentials found in session.")
            return None

        # return Credentials(
        #     token=credentials_data["token"],
        #     refresh_token=credentials_data["refresh_token"],
        #     token_uri=credentials_data["token_uri"],
        #     client_id=credentials_data["client_id"],
        #     client_secret=credentials_data["client_secret"],
        #     scopes=credentials_data["scopes"],
        # )
    
        credentials_data = json.loads(credentials_data)

        return Credentials.from_authorized_user_info(credentials_data)


    def get_authorized_session(self, credentials):
        """
        Creates an authorized session using OAuth 2.0 credentials.
        """
        authorized_session = AuthorizedSession(credentials)
        return authorized_session

    def get_flow_credentials(self, request, state):
        """
        Authorizes the user and stores the credentials in the session.
        """
        client_secret_file = self.properties.get_property("api", "client_secret_file")
        logging.info(f"Client secret file: {client_secret_file}\n"\
                     f"Request: {request}\n"\
                     f"State: {state}\n"\
                     f"  request.args: {request.args} \n" \
                     f"  request.url: {request.url}")
        flow = Flow.from_client_secrets_file(
            client_secret_file,
            scopes=['https://www.googleapis.com/auth/youtube.readonly'],
            redirect_uri='http://localhost:5000/oauth2callback'
        )
        logging.info(f"flow: {flow}\n")
        try:
            flow.fetch_token(authorization_response=request.url)
        except Exception as e:
            logging.error(f"Error fetching token: {e}")
            raise
        logging.info(f"flow.credentials: {flow.credentials.to_json}\n")
        # session["credentials"] = flow.credentials.to_json()
        # if not state == request.args["state"]:
        #     return None

        credentials = flow.credentials
        return credentials