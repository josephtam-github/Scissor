from datetime import datetime
from http import HTTPStatus

from flask import redirect, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..config.cache import cache
from ..models.links import Link
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from ..utils.urlkit import url2id

redirect_link = Blueprint(
    'Redirect Link',
    __name__,
    description='Endpoints for redirecting, caching and analyzing short links.'
)


@redirect_link.route('/<string:path>')
class Redirect(MethodView):

    @redirect_link.response(HTTPStatus.OK, description='Redirects to the true link of shortened or custom URL')
    @cache.cached()
    def get(self, path):
        """Redirects to true link of shortened or custom URL


        Turns short-link or custom link to link ID, looks up true-link with the ID, then redirects user to  true link
        """
        is_custom_link = Link.query.filter_by(custom_link=path).first()
        if is_custom_link:
            return redirect(is_custom_link.true_link, HTTPStatus.PERMANENT_REDIRECT, Response=None)
        else:
            link_id = url2id(path)

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

    if 'Referer' in request.headers:
        referer = request.headers.get('Referer')
    else:
        referer = 'Anonymous'

    short_link = request.path.replace('/', '')
    short_link_exist = Link.query.filter_by(short_link=short_link).first()

    if short_link_exist:
        # Check if IP exist and  was logged 5 minutes ago
        if ViewLog is not None:
            ip_exist = ViewLog.query.filter_by(ip_address=remote_addr). \
                filter_by(short_link=short_link).order_by(ViewLog.viewed_on.desc()).first()
            if ip_exist:
                now = datetime.now().timestamp()
                if now - ip_exist.viewed_on.timestamp() > 300:
                    log = ViewLog(
                        short_link=short_link,
                        ip_address=remote_addr,
                        referer=referer
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
                    ip_address=remote_addr,
                    referer=referer
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
