from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.String(80), nullable=False)
    secret_key = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

