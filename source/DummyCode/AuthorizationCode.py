from flask import Flask, redirect, url_for, session, request
from google_auth_oauthlib.flow import Flow
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_default_secret_key")  # Replace with a strong secret key

# OAuth 2.0 configuration
CLIENT_SECRETS_FILE = "client_secret.json"  # Replace with your client secrets file
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]  # Add any other scopes you need
REDIRECT_URI = "http://localhost:5000/callback"  # Update if your redirect URI is different

# Allow insecure transport for local development (remove in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_flow():
    """Creates and returns a Flow object for OAuth 2.0."""
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

@app.route("/")
def index():
    """Home page."""
    if "credentials" in session:
        return "You are logged in! <a href='/logout'>Logout</a>"
    else:
        return "You are not logged in. <a href='/login'>Login</a>"

@app.route("/login")
def login():
    """Redirects the user to the authorization URL."""
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # Request a refresh token
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    """Handles the callback from the authorization server."""
    state = session["state"]
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)

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

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Create a dummy client_secret.json for testing
    if not os.path.exists(CLIENT_SECRETS_FILE):
        with open(CLIENT_SECRETS_FILE, "w") as f:
            f.write('{"web": {"client_id": "YOUR_CLIENT_ID", "project_id": "YOUR_PROJECT_ID", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "YOUR_CLIENT_SECRET", "redirect_uris": ["http://localhost:5000/callback"]}}')
        logging.warning(f"Created a dummy {CLIENT_SECRETS_FILE}. Please replace with your actual client secrets.")
    app.run(debug=True)
