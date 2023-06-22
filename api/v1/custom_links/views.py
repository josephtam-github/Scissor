from sqlalchemy import func, or_
from flask import redirect, request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.links import Link
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.schemas import CustomArgSchema, LinkSchema, LinkArgSchema
from http import HTTPStatus
from flask import jsonify
from ..utils.urlkit import url2id, id2url, validate_url
from datetime import datetime

custom_link = Blueprint(
    'Custom Link',
    __name__,
    url_prefix='/custom',
    description='Endpoints for creating, updating, customizing and deleting true links.'
)


# Shorten true link
@custom_link.route('/')
class Shorten(MethodView):
    @custom_link.arguments(CustomArgSchema)
    @custom_link.response(HTTPStatus.CREATED, LinkSchema, description='Returns an object containing custom link detail')
    @jwt_required()
    def post(self, link_data):
        """Creates customized link out of original link

        Returns the details of the custom link from database
        """

        if Link is not None:
            if validate_url(link_data['custom_link']):
                custom_link_exist = Link.query.filter(or_(Link.true_link == link_data['custom_link'],
                                                          Link.custom_link == link_data['custom_link'],
                                                          Link.short_link == link_data['custom_link']
                                                          )).all()
                true_link_exist = Link.query.filter(or_(Link.true_link == link_data['true_link'],
                                                        Link.custom_link == link_data['true_link'],
                                                        Link.short_link == link_data['true_link']
                                                        )).all()
                if true_link_exist or custom_link_exist:
                    return abort(HTTPStatus.NOT_ACCEPTABLE, message='This link already exist')
                else:
                    last_item = Link.query.order_by(Link.link_id.desc()).first()

                    if last_item:
                        last_id = last_item.link_id
                    else:
                        last_id = 0

                    new_link = Link(
                        user_id=get_jwt_identity(),
                        true_link=link_data['true_link'],
                        custom_link=link_data['custom_link'],
                        short_link=id2url(int(last_id) + 1),
                    )
                    new_link.save()
                    # Create view count
                    new_count = ViewCount(
                        link_id=int(last_id) + 1,
                        short_link=id2url(int(last_id) + 1),
                    )
                    new_count.save()
                    return new_link, HTTPStatus.CREATED
            else:
                return abort(HTTPStatus.BAD_REQUEST, message='The link provided is invalid')
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')


@true_link.route('/all')
class ListAllLinks(MethodView):
    @true_link.response(HTTPStatus.OK, LinkSchema(many=True), description='Returns an object containing all link data')
    @jwt_required()
    def get(self):
        """Get a list of all user links

        Returns all links created by user
        """
        link_data = Link.query.all()

        # check if user requested course exist
        if link_data is not None:
            return link_data, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND, message='There are currently no registered links')
