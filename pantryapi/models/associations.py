from flask_sqlalchemy import SQLAlchemy
from ..database import db

# map inventory items to the ingredient they represent (kroger chicken breasts -> chicken breast)
class InventoryIngredients(db.Model):
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)

# map tags ("Greek", "chicken", "quick") to certain recipes for searching
class RecipeTags(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

# map ingredients to recipes, including the amount needed and units
class RecipeIngredients(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)

    # The 5 is arbitrary and I've never seen a recipe need more than 3 decimal places
    amount_required = db.Column(db.Numeric(5, 3))
    # setting this to text is easier than enumerating all possible units and potential abbreviations. Add to backlog?
    unit = db.Column(db.Text)
