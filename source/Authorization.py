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
        self.properties = PropertiesReader()
        # Allow insecure transport for local development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.client_secret_file = self.properties.get_property("api", "client_secret_file")
        self.scopes=['https://www.googleapis.com/auth/youtube.readonly']
        # "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"
        self.redirect_uri='http://localhost:5000/oauth2callback'

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

    def get_flow(self):
        """Creates and returns a Flow object for OAuth 2.0."""
        logging.info("get_flow: Client secret file: %s", self.client_secret_file)
        logging.info("get_flow: Scopes: %s", self.scopes)
        logging.info("get_flow: Redirect URI: %s", self.redirect_uri)

        return Flow.from_client_secrets_file(
            self.client_secret_file,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

    def get_authurl_state(self, request):
        """
        Authorizes the user and stores the credentials in the session.
        """
        
        logging.info("get_authurl_state: Client secret file: %s\nRequest: %s\n  request.args: %s\n  request.url: %s",
                    self.client_secret_file, request, request.args, request.url)
        flow = self.get_flow()
        logging.info("get_authurl_state: flow: %s\n", flow)
        authorization_url, state = flow.authorization_url(
            access_type="offline",  # Request a refresh token
            include_granted_scopes="true"
        )
        
        # try:
        #     flow.fetch_token(authorization_response=request.url)
        #     logging.info("flow: %s", flow)
        # except Exception as e:  
        #     logging.error("Error fetching token: %s", e)
        #     raise
        # logging.info(f"flow.credentials: {flow.credentials.to_json}\n")
        # # session["credentials"] = flow.credentials.to_json()
        # # if not state == request.args["state"]:
        # logging.info("flow.credentials: %s", flow.credentials.to_json)

        # credentials = flow.credentials
        # return credentials
        return authorization_url, state
    
    def get_callback(self, request):
        """
            Handles the callback from the authorization server.
        """
        state = session["state"]
        flow = self.get_flow()
        flow.fetch_token(authorization_response=request.url)
        logging.info(f"get_callback: flow.credentials: {flow.credentials.tojson}\n")
        if not state == request.args["state"]:
            return "State does not match!", 400

        credentials = flow.credentials
        session["credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }