from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

from pantryapi.resources.inventory import Inventory, InventoryList

from pantryapi.database import db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # importing the models to make sure they are known to Flask-Migrate
    from pantryapi.models.ingredient import Ingredient
    from pantryapi.models.inventoryitem import InventoryItem
    from pantryapi.models.recipe import Recipe
    from pantryapi.models.tag import Tag
    from pantryapi.models.associations import InventoryIngredients, RecipeTags, RecipeIngredients

    db.init_app(app)
    Migrate(app, db)

    # add api resources
    api = Api(app, prefix="/v1")

    api.add_resource(InventoryList, '/inventory/')
    api.add_resource(Inventory, '/inventory/<string:invid>/')

    return app