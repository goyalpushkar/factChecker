# Fact Checker Application - Enhanced with Caching, Logging, and User Authentication

# Import necessary libraries
from flask import Flask, request, jsonify, session
from transformers import pipeline
import requests
import sqlite3
import hashlib
import logging
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Load the NLP model
nlp = pipeline("text-classification", model="bert-base-uncased")

# Database initialization
def init_db():
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS facts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, claim TEXT, truth BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cache
                 (claim_hash TEXT PRIMARY KEY, result TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

# Hash the claim for caching
def get_claim_hash(claim):
    return hashlib.sha256(claim.encode()).hexdigest()

# Store result in cache
def cache_result(claim, result):
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    claim_hash = get_claim_hash(claim)
    c.execute('INSERT OR REPLACE INTO cache (claim_hash, result) VALUES (?, ?)', (claim_hash, result))
    conn.commit()
    conn.close()

# Retrieve result from cache
def get_cached_result(claim):
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    claim_hash = get_claim_hash(claim)
    c.execute('SELECT result FROM cache WHERE claim_hash = ?', (claim_hash,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Utility function to check the fact from the database
def check_fact_db(claim):
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('SELECT truth FROM facts WHERE LOWER(claim) = LOWER(?)', (claim,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# External API fact-checking (placeholder for a real fact-checking API)
def check_external_api(claim):
    api_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        'query': claim,
        'key': 'YOUR_GOOGLE_FACT_CHECK_API_KEY'
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        claims = data.get("claims", [])
        if claims:
            return claims[0].get("claimReview", [{}])[0].get("textualRating", "Unknown")
    except requests.RequestException as e:
        logging.error(f"External API error: {e}")
    return "Unknown"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()

    if result and bcrypt.check_password_hash(result[0], password):
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

    cached_result = get_cached_result(claim)
    if cached_result:
        logging.info("Cache hit")
        return jsonify({"claim": claim, "result": cached_result})

    result = check_fact_db(claim)
    if result is not None:
        logging.info("Database hit")
        cache_result(claim, str(bool(result)))
        return jsonify({"claim": claim, "truth": bool(result)})

    external_result = check_external_api(claim)
    if external_result != "Unknown":
        logging.info("External API hit")
        cache_result(claim, external_result)
        return jsonify({"claim": claim, "external_result": external_result})

    logging.info("Performing NLP analysis")
    analysis = nlp(claim)
    cache_result(claim, str(analysis))
    return jsonify({"claim": claim, "analysis": analysis})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)