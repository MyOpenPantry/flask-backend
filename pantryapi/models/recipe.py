from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ..database import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_modified = db.Column(db.DateTime, default=datetime.now)
    tags = db.relationship(
        'Tag',
        secondary='recipe_tags',
        back_populates="recipes",
    )
    ingredients = db.relationship("Association", back_populates="recipe")

    def to_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            steps = self.steps,
            notes = self.notes,
            rating = self.rating,
            created_at = self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            last_modified = self.last_modified.strftime('%Y-%m-%d %H:%M:%S')
        )
