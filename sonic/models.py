from sonic.db import db
from sqlalchemy import UniqueConstraint

class User(db.Model):
    __tablename__ = 'user'  # Explicitly name the table

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
    )

    # Define relationship to Post
    posts = db.relationship('Post', back_populates='author', cascade="all, delete-orphan")

class Post(db.Model):
    __tablename__ = 'post'  # Explicitly name the table

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)

    # Define relationship to User
    author = db.relationship('User', back_populates='posts')
