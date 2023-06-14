from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api
from .config.config import config_dict
from .utils import db, ma


def create_app(config=config_dict['test']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    ma.init_app(app)
    migrate = Migrate(app, db)

    app.config["API_TITLE"] = "Scissor"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["API_SPEC_OPTIONS"] = {
        "description": 'A flask-smorest API that allows users to shorten url links'}
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_JSON_PATH'] = 'api-spec.json'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.x/'

    api = Api(app)

    return app
