from http import HTTPStatus
from io import BytesIO
from urllib.parse import quote
from urllib.request import urlopen

from flask import jsonify
from flask import send_file
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from ..config.cache import cache
from ..models.links import Link
from ..utils.urlkit import url2id

short_link = Blueprint(
    'Short Link',
    __name__,
    url_prefix='/short',
    description='Endpoints for shortening links.'
)


@short_link.route('/<string:path>')
class Expand(MethodView):

    @short_link.response(HTTPStatus.OK, description='Returns the true link of shortened  or custom URL')
    @cache.cached(timeout=50)
    def get(self, path):
        """Returns true link of shortened or custom URL


        Turns short-link or custom-link code to link ID, looks up the true-link with the ID, then returns true link
        """
        is_custom_link = Link.query.filter_by(custom_link=path).first()
        if is_custom_link:
            return jsonify(is_custom_link.true_link)
        else:
            link_id = url2id(path)

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


@short_link.route('/qr/<string:short_link_code>')
class QRCode(MethodView):

    @short_link.response(HTTPStatus.OK, content_type='image/png', description='[JWT Required] Returns the'
                                                                              ' QR code of shortened URL in png format')
    @jwt_required()
    @cache.cached()
    def get(self, short_link_code):
        """Returns the QR code of shortened URL


        Returns the QR code of shortened URL as PNG
        """
        link_id = url2id(short_link_code)

        if not link_id:
            return abort(HTTPStatus.NOT_ACCEPTABLE, message='This short link is invalid')
        elif Link is not None:
            result_link = Link.query.filter_by(link_id=link_id).first()
            if result_link:
                quote_path = quote(result_link.short_link)
                url = "https://api.qrserver.com/v1/create-qr-code/?data={}".format(quote_path)
                print(url)
                response = urlopen(url)
                data = response.read()
                img = BytesIO(data)
                return send_file(img, mimetype='image/png')

                # return '<img src="https://api.qrserver.com/v1/create-qr-code/?data={}" alt="{}" title="{}" />'.
                # format(quote_path, result_link.true_link, 'QR Code')
            else:
                return abort(HTTPStatus.NOT_FOUND, message='Can\'t find original link')
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')
