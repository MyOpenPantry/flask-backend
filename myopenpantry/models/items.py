import sqlalchemy as sa
from sqlalchemy.orm import relationship
from myopenpantry.extensions.database import db

from datetime import datetime

# items stored in the user's pantry. Is there a better word than item? Foodstuff?
class Item(db.Model):
    __tablename__ = "items"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    # is nullable, specifically for produce since not everyone will want to use PLUS
    product_id = sa.Column(sa.Integer)
    amount = sa.Column(sa.Integer, nullable=False, default=0)
    updated = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    # Many to one, each Item is one type of ingredient (eg Item('Kroger Large Eggs') -> Ingredient('Eggs')) 
    ingredient_id = sa.Column(sa.Integer, sa.ForeignKey('ingredients.id'))
    ingredient = relationship("Ingredient", back_populates="items")
