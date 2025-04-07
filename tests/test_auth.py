import pytest
from http import HTTPStatus
from app.models.user import User

def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'username': 'newuser',
        'name': 'New User',
        'password': 'password123'
    })
    assert response.status_code == HTTPStatus.CREATED
    data = response.get_json()
    assert data['email'] == 'new@example.com'
    assert data['username'] == 'newuser'
    assert data['name'] == 'New User'
    assert 'password' not in data

def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'username': 'anotheruser',
        'name': 'Another User',
        'password': 'password123'
    })
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.get_json()['message'] == 'Email already registered'

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    response = client.post('/api/auth/register', json={
        'email': 'another@example.com',
        'username': 'testuser',
        'name': 'Another User',
        'password': 'password123'
    })
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.get_json()['message'] == 'Username already taken'

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()['message'] == 'Invalid email or password'

def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['email'] == 'test@example.com'
    assert data['username'] == 'testuser'

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get('/api/auth/me')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()['message'] == 'Token is missing'

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get('/api/auth/me', headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()['message'] == 'Token is invalid' 