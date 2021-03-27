from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ..database import db

# items stored in the user's pantry. Is there a better word than item? Foodstuff?
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    product_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    updated = db.Column(db.DateTime, default=datetime.now)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    ingredient = db.relationship(
        'Ingredient',
        secondary='inventory_ingredients',
        back_populates='inventory_items',
        uselist=False,
    )

    def to_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            product_id = self.product_id,
            amount = self.amount,
            updated = self.updated.strftime('%Y-%m-%d %H:%M:%S'),
            ingredient_id = self.ingredient_id,
        )
