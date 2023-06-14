from flask import Flask
from flask_migrate import Migrate
from .config.config import config_dict
from .utils import db, ma


def create_app(config=config_dict['test']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    ma.init_app(app)
    migrate = Migrate(app, db)

    return app
