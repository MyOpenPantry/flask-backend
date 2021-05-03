from flask_cors import CORS

from . import database
from .api import Api


def create_api(app):

    api = Api(app)
    CORS(app)

    for extension in (database,):
        extension.init_app(app)

    return api
