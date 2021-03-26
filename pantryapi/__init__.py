from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

from datetime import datetime
import logging

from pantryapi.database import db

def create_app(test_config=None):
    app = Flask(__name__)

    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    elif app.config["ENV"] == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    logging.basicConfig(
        filename=f'logs/{datetime.date(datetime.now()).isoformat()}.log', 
        level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )

    # importing the models to make sure they are known to Flask-Migrate
    from pantryapi.models.ingredient import Ingredient
    from pantryapi.models.inventoryitem import InventoryItem
    from pantryapi.models.recipe import Recipe
    from pantryapi.models.tag import Tag
    from pantryapi.models.associations import inventory_ingredients, recipe_tags, recipe_ingredients

    db.init_app(app)
    Migrate(app, db)

    # add api resources
    api = Api(app, prefix="/v1")

    from pantryapi.resources.inventory import Inventory, InventoryList
    from pantryapi.resources.recipes import Recipes, RecipesList, RecipesTags
    from pantryapi.resources.tags import Tags, TagsList

    api.add_resource(InventoryList, '/inventory/')
    api.add_resource(Inventory, '/inventory/<string:invid>/')
    api.add_resource(RecipesList, '/recipes/')
    api.add_resource(Recipes, '/recipes/<string:recid>/')
    api.add_resource(RecipesTags, '/recipes/<string:recid>/tags/')
    api.add_resource(TagsList, '/tags/')
    api.add_resource(Tags, '/tag/<string:tagid>/')

    return app
