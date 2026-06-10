# WARNING: This application is INTENTIONALLY VULNERABLE for educational purposes. DO NOT deploy to production.

import sqlite3
import os


DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app.db')


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables and seed data."""
    db = get_db()

    # Create users table
    # VULN: Password stored in PLAINTEXT - no hashing
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT,
            bio TEXT
        )
    ''')

    # Create posts table
    db.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')

    # Seed data with test user
    # VULN: Default credentials - admin/admin123, password stored in plaintext
    try:
        db.execute(
            "INSERT INTO users (username, password, email, bio) VALUES (?, ?, ?, ?)",
            ('admin', 'admin123', 'admin@secpipeline.local', 'Default administrator account')
        )
        db.execute(
            "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
            ('Welcome to SecPipeline', 'This is a demo application for DevSecOps education.', 1)
        )
        db.execute(
            "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
            ('Security Testing', 'Learn how to find and fix vulnerabilities in web applications.', 1)
        )
        db.commit()
    except sqlite3.IntegrityError:
        # Seed data already exists
        pass

    db.close()
