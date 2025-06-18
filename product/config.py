import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL2') or 'postgresql://myuser2:mypassword2@db:5433/productos'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
