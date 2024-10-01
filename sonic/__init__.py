import os
import logging

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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

    # register the database commands
    from sonic import db

    db.init_app(app)

    # apply the blueprints to the app
    from sonic import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    configure_logging(app)

    return app

def configure_logging(app):
    # Get the Flask app logger
    handler = logging.StreamHandler()
    
    # Set log level to INFO to avoid unnecessary ERROR tags
    handler.setLevel(logging.INFO)
    
    # You can also set a custom format for the logs to avoid [ERROR] appearing
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Remove the default handlers if any
    if app.logger.hasHandlers():
        app.logger.handlers.clear()
    
    # Add the customized handler
    app.logger.addHandler(handler)

    # Set the log level for the app's logger
    app.logger.setLevel(logging.INFO)