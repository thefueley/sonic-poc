import os
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy()
migrate = Migrate()

def get_db():
    """Get the current database session."""
    if "db" not in g:
        g.db = db.session  # Use the SQLAlchemy session
    return g.db

def init_app(app):
    """Register SQLAlchemy and Flask-Migrate with the Flask app."""
    db.init_app(app)
    migrate.init_app(app, db)

def init_db():
    """Initialize the database only if it does not exist."""
    db_path = os.path.join(current_app.instance_path, "sonic.sqlite")
    
    # Check if the SQLite database file already exists
    if not os.path.exists(db_path):
        with current_app.app_context():
            current_app.logger.info("Database file not found. Ensure migrations are applied using 'flask db upgrade'.")
    else:
        current_app.logger.info("Database file exists. Make sure to apply migrations if needed.")
