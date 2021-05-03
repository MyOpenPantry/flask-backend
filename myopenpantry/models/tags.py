import sqlalchemy as sa
from myopenpantry.extensions.database import db


# classify a recipe for keyword searches, eg "chicken", "french", "quick"
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(sa.Integer, primary_key=True)
    name = db.Column(sa.Text,  nullable=False, unique=True)

    recipes = db.relationship('Recipe', secondary='recipe_tags', back_populates="tags")
