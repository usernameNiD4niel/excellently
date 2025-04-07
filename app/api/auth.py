from flask import jsonify, request, current_app, Blueprint, make_response
from http import HTTPStatus
from app import db
from app.models.user import User
from app.schemas.user import user_schema, user_register_schema, user_login_schema
from datetime import datetime, UTC, timedelta
import jwt
from functools import wraps

# Create blueprint with a unique name
api = Blueprint('auth_api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check for custom header
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != 'EXCELLENTLY_API_KEY':
            return jsonify({'message': 'Invalid API key'}), HTTPStatus.UNAUTHORIZED

        # First try to get token from cookie
        token = request.cookies.get('auth_token')
        
        # If not in cookie, try Authorization header
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), HTTPStatus.UNAUTHORIZED
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.session.get(User, data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), HTTPStatus.UNAUTHORIZED
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), HTTPStatus.UNAUTHORIZED
        
        return f(current_user, *args, **kwargs)
    return decorated

@api.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate input data
    errors = user_register_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), HTTPStatus.BAD_REQUEST
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), HTTPStatus.CONFLICT
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), HTTPStatus.CONFLICT
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        name=data['name']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user_schema.dump(user)), HTTPStatus.CREATED

@api.route('/login', methods=['POST'])
def login():
    """Login user and return token."""
    data = request.get_json()
    
    # Validate input data
    errors = user_login_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), HTTPStatus.BAD_REQUEST
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), HTTPStatus.UNAUTHORIZED
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated'}), HTTPStatus.FORBIDDEN
    
    # Update last login
    user.update_last_login()
    db.session.commit()
    
    # Generate token with 24-hour expiration
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(UTC) + timedelta(hours=24)  # 24-hour expiration
    }, current_app.config['SECRET_KEY'])
    
    # Create response with user data
    response = make_response(jsonify({
        'user': user_schema.dump(user)
    }), HTTPStatus.OK)
    
    # Set secure HTTP-only cookie
    response.set_cookie(
        'auth_token',
        token,
        httponly=True,
        secure=True,  # Only sent over HTTPS
        samesite='Strict',  # Prevents CSRF
        max_age=86400  # 24 hours in seconds
    )
    
    return response

@api.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user by clearing the auth cookie."""
    response = make_response(jsonify({'message': 'Successfully logged out'}), HTTPStatus.OK)
    response.delete_cookie('auth_token')
    return response

@api.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information."""
    return jsonify(user_schema.dump(current_user)), HTTPStatus.OK 