from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ..database import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    steps = db.Column(db.Text)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_modified = db.Column(db.DateTime, default=datetime.now)
    tags = db.relationship(
        'Tag',
        secondary='recipe_tags'
    )
    ingredients = db.relationship(
        'Ingredient',
        secondary='recipe_ingredients'
    )