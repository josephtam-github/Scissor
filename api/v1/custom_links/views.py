from http import HTTPStatus

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy import or_

from ..models.links import Link
from ..models.schemas import LinkSchema, LinkArgSchema
from ..models.view_counts import ViewCount
from ..utils.urlkit import id2url, validate_url

custom_link = Blueprint(
    'Custom Link',
    __name__,
    url_prefix='/custom',
    description='Endpoints for creating, updating, customizing and deleting true links.'
)


# Shorten true link
@custom_link.route('/')
class Custom(MethodView):
    @custom_link.arguments(LinkArgSchema)
    @custom_link.response(HTTPStatus.CREATED, LinkSchema, description='[JWT Required] '
                                                                      'Returns an object containing custom link detail')
    @jwt_required()
    def post(self, link_data):
        """Creates customized link out of original link

        Returns the details of the custom link from database
        """

        if Link is not None:
            if validate_url(link_data['true_link']):
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
