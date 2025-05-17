from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    recommendations = db.relationship('Recommendation', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(100))
    cover = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0.0)
    added_by = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    recommendations = db.relationship('Recommendation', backref='book', lazy=True)

    class Recommendation(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'genre': self.genre,
            'cover': self.cover,
            'file_path': self.file_path,
            'rating': self.rating,
            'added_by': self.added_by,
            'is_public': self.is_public
        }
