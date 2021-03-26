from flask_sqlalchemy import SQLAlchemy
from ..database import db

# map inventory items to the ingredient they represent (kroger chicken breasts -> chicken breast)
inventory_ingredients = db.Table('inventory_ingredients',
    db.Column('inventory_item', db.Integer, db.ForeignKey('inventory_item.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
)

recipe_tags = db.Table('recipe_tags',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)

recipe_ingredients = db.Table('recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
    # The 5 is arbitrary and I've never seen a recipe need more than 3 decimal places
    db.Column('amount_required', db.Numeric(5, 3)),
    # setting this to text is easier than enumerating all possible units and potential abbreviations. Add to backlog?
    db.Column('unit', db.Text),
)
