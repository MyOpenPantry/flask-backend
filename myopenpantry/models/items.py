import sqlalchemy as sa
from sqlalchemy.orm import relationship
from myopenpantry.extensions.database import db

from datetime import datetime

# items stored in the user's pantry. Is there a better word than item? Foodstuff?
class Item(db.Model):
    __tablename__ = "items"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    product_id = sa.Column(sa.Integer)
    amount = sa.Column(sa.Integer)
    updated = sa.Column(sa.DateTime, default=datetime.now)
    ingredient_id = sa.Column(sa.Integer, sa.ForeignKey('ingredients.id'))
    ingredient = relationship("Ingredient", back_populates="items")

