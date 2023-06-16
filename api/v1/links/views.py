from sqlalchemy import func
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.links import Link
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


# Shorten true link
@true_link.route('/cut')
class Shorten(MethodView):
    @true_link.arguments(LinkSchema)
    @true_link.response(HTTPStatus.CREATED, LinkSchema, description='Returns an object containing short link detail')
    def post(self, link_data):
        """Shortens original link

        Returns the details of the short link from database
        """

        link_exist = Link.query.filter_by(true_link=link_data['true_link']).first()
        if link_exist or Link is None:
            abort(HTTPStatus.NOT_ACCEPTABLE, message='This link has already been shortened')
        else:
            last_id = Link.query(func.count(Link.link_id)).scalar()
            new_link = Link(
                true_link=link_data['true_link'],
                custom_link=link_data['true_link'],
                short_link=id2url(int(last_id) + 1),
            )
            new_link.save()

            return new_link, HTTPStatus.CREATED
