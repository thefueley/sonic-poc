from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app as app,
)
from werkzeug.exceptions import abort
from sqlalchemy import text
from datetime import datetime

from sonic.auth import login_required
from sonic.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = get_db().execute(
        text(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        )
    ).mappings().fetchall()

    # Convert each RowMapping to a dictionary and update 'created'
    formatted_posts = []
    for post in posts:
        post_dict = dict(post)  # Convert RowMapping to a dictionary
        if isinstance(post_dict['created'], str):
            post_dict['created'] = datetime.strptime(post_dict['created'], "%Y-%m-%d %H:%M:%S")
        formatted_posts.append(post_dict)

    app.logger.info("Fetched all posts for the index page.")
    return render_template("blog/index.html", posts=formatted_posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_db().execute(
        text(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = :id"
        ),
        {"id": id},
    ).mappings().fetchone()

    if post is None:
        app.logger.warning(f"Post with id {id} does not exist.")
        abort(404, f"Post id {id} doesn't exist.")

    # Convert RowMapping to a dictionary and update 'created'
    post_dict = dict(post)
    post_dict['created'] = datetime.strptime(post_dict['created'], "%Y-%m-%d %H:%M:%S")

    if check_author and post["author_id"] != g.user["id"]:
        app.logger.warning(
            f"User {g.user['id']} tried to access a post they don't own."
        )
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."
            app.logger.error("Post creation failed: Title is required.")

        if error is not None:
            flash(error)
            app.logger.error(f"Flashed error: {error}")
        else:
            created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
            get_db().execute(
                text("INSERT INTO post (title, body, author_id, created) VALUES (:title, :body, :author_id, :created)"),
                {"title": title, "body": body, "author_id": g.user["id"], "created": created},
            )
            get_db().commit()
            app.logger.info(f"User {g.user['id']} created a new post titled '{title}'.")
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."
            app.logger.error(f"Post update failed for post id {id}: Title is required.")

        if error is not None:
            flash(error)
            app.logger.error(f"Flashed error: {error}")
        else:
            get_db().execute(
                text("UPDATE post SET title = :title, body = :body WHERE id = :id"),
                {"title": title, "body": body, "id": id},
            )
            get_db().commit()
            app.logger.info(
                f"User {g.user['id']} updated post id {id} with new title '{title}'."
            )
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    get_db().execute(text("DELETE FROM post WHERE id = :id"), {"id": id})
    get_db().commit()
    app.logger.info(f"User {g.user['id']} deleted post id {id}.")
    return redirect(url_for("blog.index"))
