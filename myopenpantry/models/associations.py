import sqlalchemy as sa
from sqlalchemy.orm import relationship
from myopenpantry.extensions.database import db

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

recipe_tags = db.Table(
    'recipe_tags', db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


# SQLAlchemy docs say that an association table with more attributes than just the ids is best defined in a class.
# map ingredients to recipes, allowing for defined amounts in the user defined units
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'

    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = sa.Column(sa.Integer, sa.ForeignKey('ingredients.id'), primary_key=True)

    # The 5 is arbitrary and I've never seen a recipe need more than 3 decimal places
    amount = sa.Column(sa.Numeric(5, 3))
    # setting this to text is easier than enumerating all possible units and potential abbreviations
    unit = sa.Column(sa.Text)

    ingredient = relationship("Ingredient", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="ingredients")
