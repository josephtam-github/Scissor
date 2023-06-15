from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.users import User
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.schemas import LinkSchema
from http import HTTPStatus
from flask import jsonify
from ..utils.urlkit import url2id, id2url

true_link = Blueprint(
    'Link',
    __name__,
    url_prefix='/link',
    description='Endpoints for shortening, updating, and deleting true links.'
)

short_link = Blueprint(
    'Link',
    __name__,
    description='Endpoints for processing and analyzing short links.'
)
