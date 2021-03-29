"""Relational database"""

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db = SQLAlchemy()  # pylint: disable=invalid-name

def init_app(app):
    """Initialize relational database extension"""
    db.init_app(app)
    #Migrate(app, db)

    db.create_all(app=app)
