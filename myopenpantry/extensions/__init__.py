from flask_cors import CORS

from . import database
from .api import Api


def create_api(app):

    api = Api(app)
    CORS(app, resources={r"/*": {"expose_headers": ['X-Pagination', 'ETag']}})

    for extension in (database,):
        extension.init_app(app)

    return api
