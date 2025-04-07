from app import create_app
from config import Config
from flask_migrate import upgrade

app = create_app(Config)

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Run database migrations
    upgrade()
    
    # Add any other deployment tasks here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008) 