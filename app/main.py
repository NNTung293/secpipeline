# WARNING: This application is INTENTIONALLY VULNERABLE for educational purposes. DO NOT deploy to production.
# This file contains 10+ intentional security vulnerabilities for DevSecOps educational scanning.

import os
import pickle
import base64
import hashlib

import requests
from flask import (
    Flask, request, render_template, redirect, url_for,
    session, flash, jsonify, send_file, make_response
)

from app.config import Config
from app.models import get_db, init_db

# VULN: Hardcoded secret in application code
APP_SECRET = 'my-hardcoded-secret-key-do-not-share'

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
with app.app_context():
    init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Home page listing recent posts."""
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    db.close()
    return render_template('index.html', posts=posts)


@app.route('/health')
def health():
    """Health check endpoint for Docker healthcheck."""
    return jsonify({'status': 'ok'})


# VULN 1: SQL Injection - search query directly interpolated into SQL
@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = get_db()
    # VULN: Direct string formatting in SQL query - SQL Injection
    results = db.execute(
        f"SELECT * FROM posts WHERE title LIKE '%{query}%'"
    ).fetchall()
    db.close()
    # VULN 2: Reflected XSS - query is rendered with |safe in template
    return render_template('search.html', results=results, query=query)


# VULN 4: Login with SQL Injection and no rate limiting
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db()
        # VULN: SQL Injection in login - direct string formatting
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = db.execute(query).fetchone()
        db.close()

        if user:
            # VULN: Cookie set without secure or httponly flags
            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('user_id', str(user['id']))
            resp.set_cookie('username', user['username'])
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return resp
        else:
            flash('Invalid credentials', 'danger')

    # VULN 8: No CSRF token in form
    return render_template('login.html')


# VULN 3: Stored XSS - bio field rendered with |safe in template
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id') or request.cookies.get('user_id')
    if not user_id:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        bio = request.form.get('bio', '')
        # VULN: Stored XSS - bio is stored without sanitization
        db.execute(f"UPDATE users SET bio = '{bio}' WHERE id = {user_id}")
        db.commit()
        flash('Profile updated!', 'success')

    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    db.close()

    return render_template('profile.html', user=user)


# VULN 5: SSRF - Server Side Request Forgery
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    # VULN: No URL validation, can access internal services (e.g., http://169.254.169.254)
    response = requests.get(url)
    return response.text


# VULN 6: Path Traversal
@app.route('/download')
def download():
    filename = request.args.get('file', '')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    # VULN: No path validation - allows directory traversal (e.g., ../../etc/passwd)
    filepath = os.path.join('uploads', filename)
    return send_file(filepath)


# VULN 7: Insecure Deserialization
@app.route('/load-session', methods=['POST'])
def load_session():
    data = request.get_data()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    # VULN: pickle.loads on user-controlled input - Remote Code Execution
    session_data = pickle.loads(base64.b64decode(data))
    return jsonify(session_data)


# VULN 11: Weak password hashing with MD5
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = request.form.get('email', '')

    # VULN: MD5 is cryptographically broken - should use bcrypt or argon2
    password_hash = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        db.commit()
        flash('Registration successful!', 'success')
    except Exception as e:
        # VULN 10: Verbose error - leaks internal details to user
        flash(f'Registration failed: {str(e)}', 'danger')
    finally:
        db.close()

    return redirect(url_for('login'))


# VULN: Verbose error handler exposes stack traces
@app.errorhandler(500)
def internal_error(error):
    # VULN 10: Returns raw error details to the client
    return jsonify({
        'error': 'Internal Server Error',
        'details': str(error),
        'type': str(type(error).__name__)
    }), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # VULN 9: Debug mode enabled - exposes Werkzeug debugger (RCE)
    app.run(host='0.0.0.0', port=5000, debug=True)
