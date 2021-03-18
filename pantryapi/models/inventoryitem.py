from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ..database import db

# items stored in the user's pantry. Is there a better word than item? Foodstuff?
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    upc = db.Column(db.Text)
    amount = db.Column(db.Integer)
    updated = db.Column(db.DateTime, default=datetime.utcnow)
    ingredient = db.relationship(
        'Ingredient',
        secondary='inventory_ingredients'
    )