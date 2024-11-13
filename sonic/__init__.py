import os
import time
import logging

from flask import Flask, request, g
from sonic.db import db, init_app, init_db
from sonic.models import *


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Database configuration
    if os.getenv("WEBSITE_HOSTNAME"):
        # Using Azure Web App Storage
        database_uri = "sqlite:////home/sonic.sqlite"
    else:
        # Running locally
        database_uri = f"sqlite:///{os.path.join(app.instance_path, 'sonic.sqlite')}"

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Add the /version route
    @app.route("/version")
    def version():
        app_version = os.getenv("APP_VERSION", "0")
        print("Version requested.")
        return {"version": app_version}

    # register the database and migrations
    init_app(app)

    # Initialize the database only if it does not exist
    with app.app_context():
        init_db()

    # Register blueprints and other components
    from sonic import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    configure_logging(app)

    return app


# Configure logging
logging.basicConfig(level=logging.INFO)


def configure_logging(app):
    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_request(response):
        if request.path == "/favicon.ico":
            return response
        if request.path.startswith("/static"):
            return response

        now = time.time()
        duration = round(now - g.start, 2)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        host = request.host.split(":", 1)[0]
        params = dict(request.args)
        headers = dict(request.headers)

        # Limit body logging for performance and security
        try:
            body = request.get_data(as_text=True)
        except Exception as e:
            body = f"Error reading body: {e}"

        log_params = [
            ("method", request.method),
            ("path", request.path),
            ("status", response.status_code),
            ("duration", duration),
            ("ip", ip),
            ("host", host),
            ("params", params),
            ("headers", headers),
            ("body", body),
        ]

        parts = [f"{name}={value}" for name, value in log_params]
        line = " ".join(parts)

        app.logger.info(line)

        return response
