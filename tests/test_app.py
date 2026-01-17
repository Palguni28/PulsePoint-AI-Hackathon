import pytest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads correctly."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"PulsePoint AI" in rv.data

def test_static_routes(client):
    """Test that static/output routes don't crash (even if empty)."""
    rv = client.get('/outputs/non_existent.mp4')
    # Should be 404, not 500
    assert rv.status_code == 404
