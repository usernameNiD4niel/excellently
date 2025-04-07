import pytest
from app import create_app

def test_development_config():
    """Test development configuration."""
    app = create_app('development')
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False

def test_testing_config():
    """Test testing configuration."""
    app = create_app('testing')
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

def test_production_config():
    """Test production configuration."""
    app = create_app('production')
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is False

def test_default_config():
    """Test default configuration."""
    app = create_app()
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False 