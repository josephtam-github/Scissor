import flask
from sqlalchemy import func, or_
from flask import redirect, request, Response
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

redirect_link = Blueprint(
    'RedirectLink',
    __name__,
    description='Endpoints for redirecting, caching and analyzing short links.'
)


@redirect_link.route('/<string:short_link_code>')
class Redirect(MethodView):

    @redirect_link.response(HTTPStatus.OK, description='Redirects to the true link of shortened URL')
    def get(self, short_link_code):
        """Redirects to true link of shortened URL


        Turns short-link code to link ID, looks up the true-link with the ID, then redirects user to  true link
        """

        link_id = url2id(short_link_code)

        if not link_id:
            return abort(HTTPStatus.NOT_ACCEPTABLE, message='This short link is invalid')
        elif Link is not None:
            result_link = Link.query.filter_by(link_id=link_id).first()
            if result_link:
                return redirect(result_link.true_link, HTTPStatus.PERMANENT_REDIRECT, Response=None)
            else:
                return abort(HTTPStatus.NOT_FOUND, message='Can\'t find original link')
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')


@redirect_link.after_request
def after_request_callback(response):
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untraceable'
    short_link = request.path.replace('/', '')
    short_link_exist = Link.query.filter_by(short_link=short_link).first()

    if short_link_exist:
        # Check if IP exist and  was logged 5 minutes ago
        if ViewLog is not None:
            ip_exist = ViewLog.query.filter_by(ip_address=remote_addr). \
                filter_by(short_link=short_link).first()
            if ip_exist:
                now = datetime.now().timestamp()
                if now - ip_exist.viewed_on.timestamp() >= 300:
                    log = ViewLog(
                        short_link=short_link,
                        ip_address=remote_addr
                    )
                    log.save()
                    # Update view count for link
                    view_result = ViewCount.query.filter_by(short_link=short_link).first()
                    view_result.short_link = short_link
                    view_result.view_count = int(view_result.view_count) + 1
                    view_result.update()
                    return response
                else:
                    return response
            elif remote_addr != 'untraceable':
                log = ViewLog(
                    short_link=short_link,
                    ip_address=remote_addr
                )
                log.save()
                # Update view count for link
                view_result = ViewCount.query.filter_by(short_link=short_link).first()
                view_result.short_link = short_link
                view_result.view_count = int(view_result.view_count) + 1
                view_result.update()
                return response
        else:
            return response
    else:
        return response
