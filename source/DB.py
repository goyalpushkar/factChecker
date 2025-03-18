import sqlite3
import hashlib
import logging
from flask import jsonify
from flask_bcrypt import Bcrypt

class Database:

    def __init__(self):
        self.bcrypt = Bcrypt()
        self.init_db()
        self.insert_sample_facts()

    # Database initialization
    def init_db(self):
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

    # Insert sample facts
    def insert_sample_facts(self):
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
    def check_fact_db(self, claim):
        conn = sqlite3.connect('facts.db')
        c = conn.cursor()
        c.execute('SELECT truth FROM facts WHERE LOWER(claim) = LOWER(?)', (claim,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    # Hash the claim for caching
    def get_claim_hash(self, claim):
        return hashlib.sha256(claim.encode()).hexdigest()

    # Store result in cache
    def cache_result(self, claim, result):
        conn = sqlite3.connect('facts.db')
        c = conn.cursor()
        claim_hash = self.get_claim_hash(claim)
        c.execute('INSERT OR REPLACE INTO cache (claim_hash, result) VALUES (?, ?)', (claim_hash, result))
        conn.commit()
        conn.close()

    # Retrieve result from cache
    def get_cached_result(self, claim):
        conn = sqlite3.connect('facts.db')
        c = conn.cursor()
        claim_hash = self.get_claim_hash(claim)
        c.execute('SELECT result FROM cache WHERE claim_hash = ?', (claim_hash,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def create_user(self, username, password):
        hashed_password = self.bcrypt.generate_password_hash(password).decode('utf-8')
    
        conn = sqlite3.connect('facts.db')
        c = conn.cursor()
        try:
            logging.info(f"Creating User {username}")
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            logging.info(f"User {username} created")
            return jsonify({"message": "User created", "status_code": 201})
        except sqlite3.IntegrityError as e:
            logging.error(f"Error creating user {username}: {e}")
            return jsonify({"error": "User already exists", "status_code": 400})
        except Exception as e:
            logging.error(f"Error creating user {username}: {e}")
            return jsonify({"error": "Internal Server Error", "status_code": 500})  
        finally:
            conn.close()

    def verify_user(self, username, password):
        conn = sqlite3.connect('facts.db')
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        logging.info(f"User {username} found: {result}")
        conn.close()
        if result:
            return self.bcrypt.check_password_hash(result[0], password)
        return False