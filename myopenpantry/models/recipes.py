import sqlalchemy as sa
from sqlalchemy.orm import relationship
from myopenpantry.extensions.database import db

from datetime import datetime

# classify a recipe for keyword searches, eg "chicken", "french", "quick"
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(sa.Integer, primary_key=True)
    name = db.Column(sa.Text)
    recipes = db.relationship('Recipe', secondary='recipe_tags', back_populates="tags")

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(sa.Integer, primary_key=True)
    name = db.Column(sa.Text, nullable=False)
    steps = db.Column(sa.Text, nullable=False)
    notes = db.Column(sa.Text)
    rating = db.Column(sa.Integer)
    created_at = db.Column(sa.DateTime, default=datetime.now)
    last_modified = db.Column(sa.DateTime, default=datetime.now)

    # many to many
    ingredients = db.relationship("RecipeIngredients", back_populates="recipe")

    # many to many to allow filtering recipes by tags such
    tags = db.relationship('Tag', secondary='recipe_tags', back_populates="recipes")
