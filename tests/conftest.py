import pytest
import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.item import Item
from flask.testing import FlaskClient
from flask.testing import FlaskCliRunner
from flask import Flask

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_APP'] = 'app'

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def _setup_db(app: Flask):
    """Setup and cleanup database for each test."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(app: Flask) -> User:
    """Create a test user."""
    with app.app_context():
        # Clean up any existing test users
        User.query.filter_by(email='test@example.com').delete()
        db.session.commit()
        
        # Create new test user
        user = User(
            email='test@example.com',
            username='testuser',
            name='Test User',
            is_premium=False,
            is_active=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Refresh the user to ensure it's attached to the session
        db.session.refresh(user)
        return user

@pytest.fixture
def auth_headers(test_user: User, client: FlaskClient) -> dict:
    """Get authentication headers for the test user."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def other_user(app: Flask) -> User:
    """Create another test user."""
    with app.app_context():
        # Clean up any existing other users
        User.query.filter_by(email='other@example.com').delete()
        db.session.commit()
        
        # Create new other user
        user = User(
            email='other@example.com',
            username='otheruser',
            name='Other User',
            is_premium=False,
            is_active=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Refresh the user to ensure it's attached to the session
        db.session.refresh(user)
        return user 