# Fact Checker Application - Full Stack with Front-End Interface

# Import necessary libraries
from flask import Flask, redirect, request, jsonify, session, render_template, url_for
from transformers import pipeline
from DB import Database
from Logger import Logger
from Authorization import Authorization
from CaptionDerivation import CaptionDerivation
from StatementDerivation import StatementDerivation
from SummarizedStatementDerivation import SummarizedStatementDerivation
from utils import SourceTypes, CaptionSources, SummarizationTypes
from FactDerivation import FactDerivation

from readProperties import PropertiesReader
from flask_session import Session
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Create a Flask application
app = Flask(__name__)

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
loging = Logger()
logger = loging.get_logger()

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

# Load the NLP model
nlp = pipeline("text-classification", model="bert-base-uncased")

# Create a database instance
db = Database(kwargs={"logger":logger})

# Get Properties
properties = PropertiesReader(kwargs={"logger":logger})

# Get the captions from the video
captionDerivation = CaptionDerivation(kwargs={"properties":properties, "logger":logger})

# Get Statement Derivation
statementDerivation = StatementDerivation(kwargs={"properties":properties, "logger":logger})

# Get Summarized Statement Derivation
summarizedStatementDerivation = SummarizedStatementDerivation(kwargs={"properties":properties, "logger":logger})

# Get Fact Derivation
factDerivation = FactDerivation(kwargs={"properties":properties, "logger":logger})

# Get Authorizations
authorization = Authorization(kwargs={"properties":properties, "logger":logger})

@app.route('/')
def home():
    """
    Renders the home page (index.html).
    Checks if the user is authorized via Google OAuth and passes a flag to the template.
    """
    is_authorized = False
    if "credentials" in session:
        # Check if credentials are valid (you might want to add more checks here)
        try:
            credentials = authorization.get_session_credentials()
            logger.info(f"home: Credentials: {credentials}")
            if credentials and credentials.valid:
                is_authorized = True
        except Exception as e:
            logger.error(f"home: Error validating credentials: {e}")
            is_authorized = False

    return render_template('index.html', is_authorized=is_authorized)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    logger.info(f"register: Registering user: {username}")
    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    result = db.create_user(username, password)
    logger.info(f"register: User registration result: {result}")
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

@app.route('/get_captions', methods=['POST'])
def get_captions():
    # if 'user' not in session:
    #     return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    logger.info(f"get_captions: Checking caption: data: {data}")
    youtube_video_url = data.get("youtube_video_url")
    wiki_url = data.get("wiki_url")
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")
    podcast_url = data.get("podcast_url")
    raw_text = data.get("raw_text")

    if not youtube_video_url and not video_url and not audio_url and not podcast_url and not wiki_url:
        logger.warning("No url provided")
        return jsonify({"error": "No url provided"}), 400
    
    if raw_text:
        logger.warning("Captioning is not applicable")
        return jsonify({"error": "Captioning is not applicable"}), 400

    captions = None
    if youtube_video_url:
        captions = captionDerivation.get_captions(source_path=youtube_video_url, source_type=SourceTypes.YOUTUBE, caption_source=CaptionSources.ALL)
    elif video_url:
        captions = captionDerivation.get_captions(source_path=video_url, source_type=SourceTypes.VIDEO, caption_source=CaptionSources.ALL)
    elif audio_url:
        captions = captionDerivation.get_captions(source_path=audio_url, source_type=SourceTypes.AUDIO, caption_source=CaptionSources.ALL)
    elif podcast_url:
        captions = captionDerivation.get_captions(source_path=podcast_url, source_type=SourceTypes.PODCAST, caption_source=CaptionSources.ALL)
    elif wiki_url:
        captions = captionDerivation.get_wiki_captions(source_path=wiki_url)
    return jsonify({"captions": captions})

@app.route('/get_summarization', methods=['POST'])
def get_summarization():
    # if 'user' not in session:
    #     return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    logger.info(f"get_summarization: data: {data}")
    youtube_video_url = data.get("youtube_video_url")
    wiki_url = data.get("wiki_url")
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")
    podcast_url = data.get("podcast_url")
    raw_text = data.get("raw_text")

    if not youtube_video_url and not video_url and not audio_url and not podcast_url and not wiki_url and not raw_text:
        logger.warning("No text provided")
        return jsonify({"error": "No text provided"}), 400

    captions = None
    if youtube_video_url:
        captions = captionDerivation.get_captions(source_path=youtube_video_url, source_type=SourceTypes.YOUTUBE, caption_source=CaptionSources.ALL)
    elif video_url:
        captions = captionDerivation.get_captions(source_path=video_url, source_type=SourceTypes.VIDEO, caption_source=CaptionSources.ALL)
    elif audio_url:
        captions = captionDerivation.get_captions(source_path=audio_url, source_type=SourceTypes.AUDIO, caption_source=CaptionSources.ALL)
    elif podcast_url:
        captions = captionDerivation.get_captions(source_path=podcast_url, source_type=SourceTypes.PODCAST, caption_source=CaptionSources.ALL)
    elif wiki_url:
        captions = captionDerivation.get_wiki_captions(source_path=wiki_url)
        # captions = all_captions["wikicontent"]
    elif raw_text:
        captions = raw_text

    logger.info(f"get_summarization: captions: {captions}")
    if not captions:
        logger.warning("Not able to get captions/ transcript for Summarization")
        return jsonify({"error": "Not able to get captions/ transcript for Summarization"}), 400

    # Get summarizd text
    summarized_text = summarizedStatementDerivation.get_summarized_statements(captions, summary_type=SummarizationTypes.ABSTRACTIVE_SUMMARY)
    return jsonify({"summarized_text": summarized_text})

@app.route('/get_statements', methods=['POST'])
def get_statements():
    # if 'user' not in session:
    #     return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    logger.info(f"get_statements: data: {data}")
    youtube_video_url = data.get("youtube_video_url")
    wiki_url = data.get("wiki_url")
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")
    podcast_url = data.get("podcast_url")
    raw_text = data.get("raw_text")

    if not youtube_video_url and not video_url and not audio_url and not podcast_url and not wiki_url and not raw_text:
        logger.warning("No text provided")
        return jsonify({"error": "No text provided"}), 400

    captions = None
    if youtube_video_url:
        captions = captionDerivation.get_captions(source_path=youtube_video_url, source_type=SourceTypes.YOUTUBE, caption_source=CaptionSources.ALL)
    elif video_url:
        captions = captionDerivation.get_captions(source_path=video_url, source_type=SourceTypes.VIDEO, caption_source=CaptionSources.ALL)
    elif audio_url:
        captions = captionDerivation.get_captions(source_path=audio_url, source_type=SourceTypes.AUDIO, caption_source=CaptionSources.ALL)
    elif podcast_url:
        captions = captionDerivation.get_captions(source_path=podcast_url, source_type=SourceTypes.PODCAST, caption_source=CaptionSources.ALL)
    elif wiki_url:
        captions = captionDerivation.get_wiki_url_text(wiki_url)
    elif raw_text:
        captions = raw_text

    logger.info(f"get_statements: captions: {captions}")
    if not captions:
        logger.warning("Not able to get captions/ transcript for Factual Statements")
        return jsonify({"error": "Not able to get captions/ transcript for Factual Statements"}), 400

    factual_statements = statementDerivation.get_factual_statements(captions, "nltk")
    return jsonify({"factual_statements": factual_statements})

@app.route('/check', methods=['POST'])
def fact_check():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    claim = data.get("claim")

    if not claim:
        logger.warning("No claim provided")
        return jsonify({"error": "No claim provided"}), 400

    logger.info(f"fact_check: Checking claim: {claim}")

    cached_result = db.get_cached_result(claim)
    if cached_result:
        logger.info("fact_check: Cache hit")
        return jsonify({"claim": claim, "result": cached_result})

    result = db.check_fact_db(claim)
    if result is not None:
        logger.info("fact_check: Database hit")
        db.cache_result(claim, str(bool(result)))
        return jsonify({"claim": claim, "truth": bool(result)})

    external_result = factDerivation.check_external_api(claim)
    if external_result != "Unknown":
        logger.info("fact_check: External API hit")
        db.cache_result(claim, external_result)
        return jsonify({"claim": claim, "external_result": external_result})

    logger.info("fact_check: Performing NLP analysis")
    analysis = nlp(claim)
    db.cache_result(claim, str(analysis))
    return jsonify({"claim": claim, "analysis": analysis})

# User clicks "Authorize with Google" on index.html.
# oauth2authorize route is called, which redirects to Google's authorization page.
# User grants permission on Google's page.
# Google redirects back to your oauth2callback route.
# oauth2callback processes the callback, fetches the token, and stores credentials in the session.
# oauth2callback then redirects the user to the home route (/).
# The browser loads the index.html template, which is the main page
@app.route("/oauth2authorize")
def oauth2authorize():
    """
    Redirect the user to Google's authorization page.
    """
    # state = os.urandom(16).hex()
    authorization_url, state =  authorization.get_authurl_state(request)
    logger.info(f"oauth2authorize: Authorization URL: {authorization_url} \n: State: {state}")
    session["state"] = state
    
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    """
    Handle the callback from Google after the user grants permission.
    """
    authorization.get_callback(request)
    logger.info("oauth2callback: Callback received")
    return redirect(url_for("home")) # redirect(url_for("home"))

@app.route('/authorized', methods=['GET', 'POST'])
def authorized():
    return render_template('index.html')
    #jsonify({"message": "Authorized successfully"})

if __name__ == '__main__':
    # Database = Database()
    app.run(debug=True)