import os
import time
import logging

from flask import Flask, request, g


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Determine the database path based on the environment
    if os.getenv("WEBSITE_HOSTNAME"):
        # Running on Azure Web App Service
        database_path = os.path.join("/home", "sonic.sqlite")
    else:
        # Running locally
        database_path = os.path.join(app.instance_path, "sonic.sqlite")

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        DATABASE=database_path,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # Add the /version route
    @app.route("/version")
    def version():
        app_version = os.getenv("APP_VERSION", "😵")
        return {"version": app_version}

    # register the database commands
    from sonic import db

    db.init_app(app)

    # apply the blueprints to the app
    from sonic import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint="index")

    # Add logging middleware
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
