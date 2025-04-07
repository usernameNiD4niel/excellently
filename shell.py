from app import create_app, db
from app.models.user import User
from app.models.item import Item
from config import Config

app = create_app(Config)

def shell_context():
    """Create shell context with database models."""
    return {
        'app': app,
        'db': db,
        'User': User,
        'Item': Item,
        'session': db.session
    }

if __name__ == '__main__':
    from IPython import embed
    with app.app_context():
        embed(user_ns=shell_context()) 