from flask_sqlalchemy import SQLAlchemy
from ..database import db

class PantryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    upc = db.Column(db.String(12))
    amount = db.Column(db.Integer)
    updated = db.Column(db.DateTime)