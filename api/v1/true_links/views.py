from http import HTTPStatus

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy import func

from ..models.links import Link
from ..models.schemas import LinkDetail
from ..models.schemas import LinkSchema, LinkArgSchema
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from ..utils.urlkit import id2url, validate_url

true_link = Blueprint(
    'True Link',
    __name__,
    url_prefix='/link',
    description='Endpoints for updating, customizing and deleting true links.'
)


# Shorten true link
@true_link.route('/')
class Shorten(MethodView):
    @true_link.arguments(LinkArgSchema)
    @true_link.response(HTTPStatus.CREATED, LinkSchema, description='[JWT Required] Returns an object'
                                                                    ' containing short link detail')
    @jwt_required()
    def post(self, link_data):
        """Shortens original link [JWT Required]

        Returns the details of the short link from database
        """

        if Link is not None:
            if validate_url(link_data['true_link']):
                link_exist = Link.query.filter_by(true_link=link_data['true_link']).first()
                if link_exist:
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
                        custom_link=link_data['true_link'],
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
    @true_link.response(HTTPStatus.OK, LinkSchema(many=True), description='[JWT Required] '
                                                                          'Returns an object containing all link data')
    @jwt_required()
    def get(self):
        """Get a list of all user links [JWT Required]

        Returns all links created by user
        """
        link_data = Link.query.all()

        # check if user requested course exist
        if link_data is not None:
            return link_data, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND, message='There are currently no registered links')


@true_link.route('/detail/<string:link_id>')
class GetLinkDetail(MethodView):
    @true_link.response(HTTPStatus.OK, LinkDetail(many=True), description='[JWT Required] '
                                                                          'Returns a list of tuples where each tuple'
                                                                          ' contains the referer and its corresponding'
                                                                          ' link count')
    @jwt_required()
    def get(self, link_id):
        """Get a list referers and corresponding link count for a link [JWT Required]

        Returns a list of tuples where each tuple contains the referer and its corresponding link count
        """
        # check if link exists
        link_exist = ViewLog.query.filter_by(view_log_id=link_id).first()
        # Query the database to get the link count by referer
        if link_exist:
            link_detail = ViewLog.query.with_entities(ViewLog.referer, func.count(ViewLog.referer).label('clicks'))\
                .filter_by(short_link=link_exist.short_link)\
                .group_by(ViewLog.referer)\
                .all()

            # check if user requested course exist
            if link_detail is not None:
                return link_detail, HTTPStatus.OK
            else:
                abort(HTTPStatus.NOT_FOUND, message='There are currently no details for this links')
        else:
            abort(HTTPStatus.NOT_FOUND, message='The link id provided does not exist')
