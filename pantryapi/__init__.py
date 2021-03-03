from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

from pantryapi.resources.items import Items

from pantryapi.database import db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'

    db.init_app(app)
    Migrate(app, db)

    api = Api(app)

    #api.add_resource(Items, '/items/')
    api.add_resource(Items, '/items/<string:piname>/')

    # importing the models to make sure they are known to Flask-Migrate
    from pantryapi.models.pantryitem import PantryItem

    # any other registrations; blueprints, template utilities, commands

    return app