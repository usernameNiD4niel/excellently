from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.api.auth import api as auth_api
    from app.api.users import api as users_api
    from app.api.excel import api as excel_api
    
    app.register_blueprint(auth_api, url_prefix='/auth')
    app.register_blueprint(users_api, url_prefix='/api')
    app.register_blueprint(excel_api, url_prefix='/api')

    # Serve static files
    @app.route('/')
    def index():
        return render_template('index.html')

    return app 