import sqlalchemy as sa
from sqlalchemy.orm import relationship
from myopenpantry.extensions.database import db

# ingredients are a base part of recipes. ex "chicken breast"
# association tables will be used to join these with inventory items, as well as the amount needed in recipes
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), nullable=False, unique=True)

    # many to one, with Ingredient being the one 
    items = relationship('Item', back_populates="ingredient")
    # many to many
    recipes = relationship("RecipeIngredients", back_populates="ingredient")
