from flask import jsonify
from http import HTTPStatus

def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), HTTPStatus.NOT_FOUND

def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end'
    }), HTTPStatus.INTERNAL_SERVER_ERROR 