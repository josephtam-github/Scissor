from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from .config.config import config_dict
from .models.blocklist import TokenBlocklist
from .utils import db, ma


def create_app(config=config_dict['dev']):
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

    jwt = JWTManager(app)

    # Callback function to check if a JWT exists in the database blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

        return token is not None

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'ma': ma,
        }

    return app
