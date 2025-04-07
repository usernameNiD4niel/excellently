from flask import jsonify, request
from http import HTTPStatus
from app import db
from app.models import Item
from app.schemas import item_schema, items_schema
from app.api import api
from app.api.auth import token_required

@api.route('/health', methods=['GET'])
@token_required
def health_check(current_user):
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'user': current_user.username
    }), HTTPStatus.OK

@api.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify(items_schema.dump(items)), HTTPStatus.OK

@api.route('/items', methods=['POST'])
@token_required
def create_item(current_user):
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Name is required'
        }), HTTPStatus.BAD_REQUEST
    
    item = Item(name=data['name'], owner=current_user)
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item_schema.dump(item)), HTTPStatus.CREATED 