from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from ..database import db
from datetime import datetime

# map inventory items to the ingredient they represent (kroger chicken breasts -> chicken breast)
inventory_ingredients = db.Table('inventory_ingredients',
    db.Column('inventory_item', db.Integer, db.ForeignKey('inventory_item.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
)

recipe_tags = db.Table('recipe_tags',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
)
"""
Base = declarative_base()
class RecipeIngredients(Base):
    __tablename__ = 'RecipeIngredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    # The 5 is arbitrary and I've never seen a recipe need more than 3 decimal places
    amount_required = db.Column(db.Numeric(5, 3))
    # setting this to text is easier than enumerating all possible units and potential abbreviations. Add to backlog?
    unit = db.Column(db.Text)
    ingredient = db.relationship('Ingredient', back_populates='recipes')
    recipe = db.relationship('Recipe', back_populates='ingredients')
"""
#recipe_ingredients = db.Table('recipe_ingredients',
#    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
#    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
    # The 5 is arbitrary and I've never seen a recipe need more than 3 decimal places
#    db.Column('amount_required', db.Numeric(5, 3)),
    # setting this to text is easier than enumerating all possible units and potential abbreviations. Add to backlog?
#    db.Column('unit', db.Text),
#)

class Association(db.Model):
    __tablename__ = 'association'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    amount = db.Column(db.Numeric(5, 3))
    # setting this to text is easier than enumerating all possible units and potential abbreviations. Add to backlog?
    unit = db.Column(db.Text)
    ingredient = db.relationship("Ingredient", back_populates="recipes")
    recipe = db.relationship("Recipe", back_populates="ingredients")
