import pytest
from http import HTTPStatus
from app.models.user import User
from app import db

def test_get_users_unauthorized(client):
    """Test getting all users without premium access."""
    response = client.get('/api/users')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()['message'] == 'Token is missing'

def test_get_users_premium(client, auth_headers, test_user, app):
    """Test getting all users with premium access."""
    with app.app_context():
        # Get a fresh reference to the user in the current session
        user = db.session.get(User, test_user.id)
        # Make user premium
        user.is_premium = True
        db.session.commit()
    
    response = client.get('/api/users', headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['email'] == test_user.email

def test_get_user_own_profile(client, auth_headers, test_user):
    """Test getting own user profile."""
    response = client.get(f'/api/users/{test_user.id}', headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['id'] == test_user.id
    assert data['email'] == test_user.email

def test_get_user_other_profile(client, auth_headers, test_user, other_user):
    """Test getting other user's profile without premium access."""
    response = client.get(f'/api/users/{other_user.id}', headers=auth_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.get_json()['message'] == 'Access denied'

def test_update_user_own_profile(client, auth_headers, test_user, app):
    """Test updating own user profile."""
    response = client.put(f'/api/users/{test_user.id}', 
                         headers=auth_headers,
                         json={'name': 'Updated Name'})
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['name'] == 'Updated Name'
    
    # Verify the change in database
    with app.app_context():
        updated_user = db.session.get(User, test_user.id)
        assert updated_user.name == 'Updated Name'

def test_update_user_other_profile(client, auth_headers, test_user, other_user):
    """Test updating other user's profile without premium access."""
    response = client.put(f'/api/users/{other_user.id}',
                         headers=auth_headers,
                         json={'name': 'Updated Name'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.get_json()['message'] == 'Access denied'

def test_delete_user_own_profile(client, auth_headers, test_user, app):
    """Test deleting own user profile."""
    response = client.delete(f'/api/users/{test_user.id}', headers=auth_headers)
    assert response.status_code == HTTPStatus.NO_CONTENT
    
    # Verify user is soft deleted
    with app.app_context():
        user = db.session.get(User, test_user.id)
        assert user.is_deleted is True
        assert user.is_active is False

def test_delete_user_other_profile(client, auth_headers, test_user, other_user):
    """Test deleting other user's profile without premium access."""
    response = client.delete(f'/api/users/{other_user.id}', headers=auth_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.get_json()['message'] == 'Access denied' 