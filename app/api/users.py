from flask import jsonify, request, Blueprint
from http import HTTPStatus
from app import db
from app.models.user import User
from app.schemas.user import user_schema, users_schema
from app.api.auth import token_required

# Create blueprint with a unique name
api = Blueprint('users_api', __name__)

@api.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users."""
    users = User.query.all()
    return jsonify(users_schema.dump(users)), HTTPStatus.OK

@api.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get a specific user."""
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user)), HTTPStatus.OK

@api.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update a user."""
    # Only allow users to update their own profile
    if current_user.id != user_id:
        return jsonify({'message': 'Unauthorized'}), HTTPStatus.FORBIDDEN
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user_schema.dump(user)), HTTPStatus.OK

@api.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Delete a user."""
    # Only allow users to delete their own profile
    if current_user.id != user_id:
        return jsonify({'message': 'Unauthorized'}), HTTPStatus.FORBIDDEN
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT 