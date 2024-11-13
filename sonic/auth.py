import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app as app,
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from sonic.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        app.logger.info("No user logged in.")
    else:
        g.user = get_db().execute(
            text("SELECT * FROM user WHERE id = :id"), {"id": user_id}
        ).mappings().fetchone()
        if g.user:
            app.logger.info(f"User {g.user['username']} (ID: {user_id}) logged in.")
        else:
            app.logger.warning(f"User with id {user_id} failed login.")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user with an email and role."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role", "student")
        error = None

        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                get_db().execute(
                    text("INSERT INTO user (username, email, password, role) VALUES (:username, :email, :password, :role)"),
                    {"username": username, "email": email, "password": generate_password_hash(password), "role": role},
                )
                get_db().commit()
                app.logger.info(f"User {username} registered successfully.")
            except Exception as e:
                error = "Registration failed."
                app.logger.warning(f"User {username} registration failed: {str(e)}")

            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)
        app.logger.error(f"User {username} registration failed: {error}")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = get_db().execute(
            text("SELECT * FROM user WHERE username = :username"), {"username": username}
        ).mappings().fetchone()

        if user is None:
            error = "Incorrect username."
            app.logger.warning(f"Login attempt failed: {error} for username {username}")
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
            app.logger.warning(f"Login attempt failed: {error} for username {username}")

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            app.logger.info(f"User {username} logged in successfully.")
            return redirect(url_for("index"))

        flash(error)
        app.logger.error(f"Login error: {error}")

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
