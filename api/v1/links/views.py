from sqlalchemy import func, or_
from flask import redirect
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

true_link = Blueprint(
    'Link',
    __name__,
    url_prefix='/link',
    description='Endpoints for updating, customizing and deleting true links.'
)

short_link = Blueprint(
    'Link',
    __name__,
    description='Endpoints for shortening, redirecting, caching and analyzing short links.'
)


# Shorten true link
@short_link.route('/')
class Shorten(MethodView):
    @short_link.arguments(LinkArgSchema)
    @short_link.response(HTTPStatus.CREATED, LinkSchema, description='Returns an object containing short link detail')
    @jwt_required()
    def post(self, link_data):
        """Shortens original link

        Returns the details of the short link from database
        """

        link_exist = Link.query.filter_by(true_link=link_data['true_link']).first()

        if link_exist:
            return
            abort(HTTPStatus.NOT_ACCEPTABLE, message='This link already exist')
        elif Link is not None:
            last_item = Link.query.order_by(Link.link_id.desc()).first()
            if last_item:
                last_id = last_item.link_id
            else:
                last_id = 0

            new_link = Link(
                user_id=get_jwt_identity(),
                true_link=link_data['true_link'],
                custom_link=link_data['true_link'],
                short_link=id2url(int(last_id) + 1),
            )
            new_link.save()

            return new_link, HTTPStatus.CREATED
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')


@short_link.route('/<string:short_link_code>')
class Expand(MethodView):

    @true_link.response(HTTPStatus.OK, description='Returns the true link of shortened URL')
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
