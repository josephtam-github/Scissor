from sqlalchemy import func, or_
from flask import redirect, request, Response, make_response, send_file
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
from urllib.parse import quote
from urllib.request import urlopen
from datetime import datetime
from PIL import Image
from io import BytesIO

short_link = Blueprint(
    'Short Link',
    __name__,
    url_prefix='/short',
    description='Endpoints for shortening links.'
)


@short_link.route('/<string:short_link_code>')
class Expand(MethodView):

    @short_link.response(HTTPStatus.OK, description='Returns the true link of shortened  or custom URL')
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

    @short_link.response(HTTPStatus.OK, content_type='image/png', description='Returns the QR code of shortened URL')
    @jwt_required()
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

                # return '<img src="https://api.qrserver.com/v1/create-qr-code/?data={}" alt="{}" title="{}" />'.format(quote_path, result_link.true_link, 'QR Code')
            else:
                return abort(HTTPStatus.NOT_FOUND, message='Can\'t find original link')
        else:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='Internal server error please try again later')
