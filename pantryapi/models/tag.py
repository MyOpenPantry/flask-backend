from flask_sqlalchemy import SQLAlchemy
from ..database import db

# classify a recipe for keyword searches, eg "chicken", "french", "quick"
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    recipes = db.relationship(
        'Recipe',
        secondary='recipe_tags',
        back_populates="tags"
    )

    def to_dict(self):
        return dict(
            id = self.id,
            name = self.name,
        )
