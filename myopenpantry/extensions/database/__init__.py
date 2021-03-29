"""Relational database"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()  # pylint: disable=invalid-name

def init_app(app):
    """Initialize relational database extension"""
    db.init_app(app)
    #Migrate(app, db)

    db.create_all(app=app)
