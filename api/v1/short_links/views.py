from sqlalchemy import func, or_
from flask import redirect, request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.links import Link
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.schemas import LinkSchema, LinkArgSchema
from http import HTTPStatus
from flask import jsonify
from ..utils.urlkit import url2id, id2url
from datetime import datetime

short_link = Blueprint(
    'Link',
    __name__,
    url_prefix='/short',
    description='Endpoints for shortening links.'
)


@short_link.route('/<string:short_link_code>')
class Expand(MethodView):

    @short_link.response(HTTPStatus.OK, description='Returns the true link of shortened URL')
    def get(self, short_link_code):
        """Returns true link of shortened URL


        Turns short-link code to link ID, looks up the true-link with the ID, then returns true link
        """

        link_id = url2id(short_link_code)

        if not link_id:
            return abort(HTTPStatus.NOT_ACCEPTABLE, message='This short link is invalid')
        elif Link is not None:
            result_link = Link.query.filter_by(link_id=link_id).first()
            if result_link:
                return jsonify(result_link.true_link)
            else:
                return abort(HTTPStatus.NOT_FOUND, message='Can\'t find original link')
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')
