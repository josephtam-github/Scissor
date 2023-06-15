from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.users import User
from ..models.schemas import UserSchema, LinkSchema, ViewCountSchema, ViewLogSchema
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint(
    'Auth',
    __name__,
    url_prefix='/auth',
    description='Authentication for user registration and login with JWT token'
)
