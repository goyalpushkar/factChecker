# Fact Checker Application - Expanded Version with External API Integration

# Import necessary libraries
from flask import Flask, request, jsonify
from transformers import pipeline
import requests
import sqlite3

app = Flask(__name__)

# Load the NLP model
nlp = pipeline("text-classification", model="bert-base-uncased")

# Database initialization
def init_db():
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS facts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, claim TEXT, truth BOOLEAN)''')
    conn.commit()
    conn.close()

# Insert sample facts
def insert_sample_facts():
    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    sample_facts = [
        ("The earth is round", True),
        ("The sky is green", False)
    ]
    c.executemany('INSERT INTO facts (claim, truth) VALUES (?, ?)', sample_facts)
    conn.commit()
    conn.close()

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
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        claims = data.get("claims", [])
        if claims:
            return claims[0].get("claimReview", [{}])[0].get("textualRating", "Unknown")
    return "Unknown"

@app.route('/check', methods=['POST'])
def fact_check():
    data = request.json
    claim = data.get("claim")

    if not claim:
        return jsonify({"error": "No claim provided"}), 400

    # Check against the database
    result = check_fact_db(claim)
    if result is not None:
        return jsonify({"claim": claim, "truth": bool(result)})

    # Check against external fact-checking API
    external_result = check_external_api(claim)
    if external_result != "Unknown":
        return jsonify({"claim": claim, "external_result": external_result})

    # Perform NLP-based analysis
    analysis = nlp(claim)
    return jsonify({"claim": claim, "analysis": analysis})

@app.route('/add_fact', methods=['POST'])
def add_fact():
    data = request.json
    claim = data.get("claim")
    truth = data.get("truth")

    if not claim or truth is None:
        return jsonify({"error": "Invalid input"}), 400

    conn = sqlite3.connect('facts.db')
    c = conn.cursor()
    c.execute('INSERT INTO facts (claim, truth) VALUES (?, ?)', (claim, truth))
    conn.commit()
    conn.close()

    return jsonify({"message": "Fact added successfully"}), 201

if __name__ == '__main__':
    init_db()
    insert_sample_facts()
    app.run(debug=True)
