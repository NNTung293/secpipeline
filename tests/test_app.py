# WARNING: This application is INTENTIONALLY VULNERABLE for educational purposes. DO NOT deploy to production.

import json
import sys
import os
import pytest

# Ensure the app module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_returns_200(client):
    """Test that the home page returns HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_health_returns_json(client):
    """Test that /health returns JSON with status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_search_returns_200(client):
    """Test that /search returns HTTP 200."""
    response = client.get('/search')
    assert response.status_code == 200


def test_search_with_query(client):
    """Test that /search with a query parameter returns HTTP 200."""
    response = client.get('/search?q=test')
    assert response.status_code == 200


def test_login_get_returns_200(client):
    """Test that /login GET returns the login form."""
    response = client.get('/login')
    assert response.status_code == 200


def test_login_post_invalid_credentials(client):
    """Test that /login POST with bad credentials redirects or shows error."""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
