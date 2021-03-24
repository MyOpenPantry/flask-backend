from flask_sqlalchemy import SQLAlchemy
from ..database import db

# ingredients are a base part of recipes. ex "chicken breast"
# association tables will be used to join these with inventory items, as well as the amount needed in recipes
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    recipes = db.relationship(
        'Recipe',
        secondary='recipe_ingredients'
    )
    inventory_items = db.relationship(
        'InventoryItem',
        secondary='inventory_ingredients'
    )
