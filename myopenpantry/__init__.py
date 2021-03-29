from flask import Flask

from datetime import datetime
import logging

from myopenpantry.config import app_config
from myopenpantry import extensions, views

def create_app(config_name):
    app = Flask(__name__)

    if config_name in app_config:
        app.config.from_object(app_config[config_name])
    else:
        app.config.from_object(app_config['development'])

    api = extensions.create_api(app)
    views.register_blueprints(api)

    logging.basicConfig(
        filename=f'logs/{datetime.date(datetime.now()).isoformat()}.log', 
        level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )

    return app
