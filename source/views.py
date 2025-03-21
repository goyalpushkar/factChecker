# Fact Checker Application - Full Stack with Front-End Interface

# Import necessary libraries
import os
from flask import Flask, redirect, request, jsonify, session, render_template, url_for
from transformers import pipeline
import requests
import logging
from flask_bcrypt import Bcrypt
from flask_session import Session
from DB import Database
from FactDerivation import FactDerivation
from CaptionDerivation import CaptionDerivation
from Authorization import Authorization
from readProperties import PropertiesReader
from google_auth_oauthlib.flow import Flow

# Create a Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask session configuration
# Specifies which type of session interface to use. Built-in session types:
# – null: NullSessionInterface (default)
# – redis: RedisSessionInterface
# – memcached: MemcachedSessionInterface
# – mongodb: MongoDBSessionInterface
# – sqlalchemy: SqlAlchemySessionInterface
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 600

Session(app)

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Load the NLP model
nlp = pipeline("text-classification", model="bert-base-uncased")

# Create a database instance
db = Database()

# Get Properties
properties = PropertiesReader("config.properties")

# Get the captions from the video
captionDerivation = CaptionDerivation()

# Get Fact Derivation
factDerivation = FactDerivation()

# Get Authorizations
authorization = Authorization()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    logging.info(f"Registering user: {username}")
    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    result = db.create_user(username, password)
    logging.info(f"User registration result: {result}")
    return result
    # if result.status_code == 201:
    #     return jsonify({"message": "User registered successfully"}), 201
    # else:
    #     return jsonify({"error": "User already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    result = db.verify_user(username, password)

    if result:
        session['user'] = username
        return jsonify({"message": "Login successful"})

    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logout successful"})

@app.route('/check', methods=['POST'])
def fact_check():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    claim = data.get("claim")

    if not claim:
        logging.warning("No claim provided")
        return jsonify({"error": "No claim provided"}), 400

    logging.info(f"Checking claim: {claim}")

    cached_result = db.get_cached_result(claim)
    if cached_result:
        logging.info("Cache hit")
        return jsonify({"claim": claim, "result": cached_result})

    result = db.check_fact_db(claim)
    if result is not None:
        logging.info("Database hit")
        db.cache_result(claim, str(bool(result)))
        return jsonify({"claim": claim, "truth": bool(result)})

    external_result = factDerivation.check_external_api(claim)
    if external_result != "Unknown":
        logging.info("External API hit")
        db.cache_result(claim, external_result)
        return jsonify({"claim": claim, "external_result": external_result})

    logging.info("Performing NLP analysis")
    analysis = nlp(claim)
    db.cache_result(claim, str(analysis))
    return jsonify({"claim": claim, "analysis": analysis})

@app.route('/get_captions', methods=['POST'])
def get_captions():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    video_url = data.get("video_url")

    if not video_url:
        logging.warning("No video url provided")
        return jsonify({"error": "No video url provided"}), 400

    logging.info(f"Checking caption: {video_url}")

    captions = captionDerivation.get_captions(video_url, "google")
    return jsonify({"captions": captions})

@app.route("/oauth2authorize")
def oauth2authorize():
    """
    Redirect the user to Google's authorization page.
    """
    state = os.urandom(16).hex()
    authorization_url, state = authorization.get_flow_credentials(request, state).authorization_url(
        access_type="offline",  # Request a refresh token
        include_granted_scopes="true",
        state=state
    )
    session["state"] = state
    logging.info(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    """
    Handle the callback from Google after the user grants permission.
    """
    state = None
    logging.info(f"Request: {request}\n State: {state} \n Session: {session}")
    if "state" in session:
        state = session["state"]
    credentials = authorization.get_flow_credentials(request, state)

    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    return redirect(url_for("home"))

if __name__ == '__main__':
    # Database = Database()
    app.run(debug=True)