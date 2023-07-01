from sqlalchemy import or_
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.users import User
from ..models.schemas import UserSchema, LinkSchema, LoginArgSchema, LoginResponseSchema, ViewCountSchema, ViewLogSchema
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, \
    get_jwt_identity, get_jwt
from flask import jsonify
from datetime import datetime, timezone
from ..models.blocklist import TokenBlocklist

auth = Blueprint(
    'Auth',
    __name__,
    url_prefix='/auth',
    description='Authentication for user registration and login with JWT token'
)


@auth.route('/register')
class Register(MethodView):
    @auth.arguments(UserSchema)
    @auth.response(HTTPStatus.CREATED, UserSchema, description='Returns an object containing '
                                                               'the created user\'s detail')
    def post(self, new_data):
        """Register a new user

        Returns the new user info from the database
        """
        # Check if username and email exists
        email_exist = User.query.filter_by(email=new_data['email']).first()
        username_exist = User.query.filter_by(username=new_data['username']).first()
        if email_exist or username_exist:
            abort(HTTPStatus.NOT_ACCEPTABLE, message='This email or username already exists')
        else:
            new_user = User(
                username=new_data['username'].lower(),
                firstname=new_data['firstname'].lower(),
                lastname=new_data['lastname'].lower(),
                email=new_data['email'].lower(),
                password_hash=generate_password_hash(new_data['password']),
                )
            new_user.save()

        return new_user, HTTPStatus.CREATED


@auth.route('/login')
class Login(MethodView):
    @auth.arguments(LoginArgSchema)
    @auth.response(HTTPStatus.ACCEPTED, LoginResponseSchema, description='Returns the access and return tokens')
    def post(self, login_data):
        """Logs in user

        Returns access and refresh tokens
        """

        if 'email' in login_data.keys():
            email = login_data['email'].lower()
            user = User.query.filter_by(email=email).first()
        elif 'username' in login_data.keys():
            username = login_data['username'].lower()
            user = User.query.filter_by(email=email).first()
        else:
            abort(HTTPStatus.BAD_REQUEST, message='You must input either your username or your email '
                                                  'along with your password')
        password = login_data['password']

        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.user_id)
            refresh_token = create_refresh_token(identity=user.user_id)
            response = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            return jsonify(response), HTTPStatus.ACCEPTED
        else:
            abort(HTTPStatus.UNAUTHORIZED, message='Invalid credentials')


@auth.route('/logout')
class Logout(MethodView):
    @auth.response(HTTPStatus.OK, description='Returns success message')
    @jwt_required()
    def delete(self):
        """Log the User Out

        Returns success message
        """
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        blocked_token = TokenBlocklist(jti=jti, created_at=now)
        blocked_token.save()
        return {"message": "Logout successful"}, HTTPStatus.OK


@auth.route('/refresh')
class Refresh(MethodView):
    @auth.response(HTTPStatus.OK, description='Returns a new access token')
    @jwt_required(refresh=True)
    def post(self):
        """Generate Refresh Token

        Returns new access token
        """
        user_id = get_jwt_identity()
        claims = get_jwt()
        access_token = create_access_token(identity=user_id, additional_claims=claims)
        return jsonify({'access_token': access_token}), HTTPStatus.OK


@auth.route('/user')
class Register(MethodView):
    @auth.response(HTTPStatus.OK, UserSchema, description='Returns an object containing '
                   'the user\'s detail')
    @jwt_required()
    def get(self):
        """Returns user details

        Returns the user info from access token
        """
        # Get details from user id
        user_id = get_jwt_identity()
        user_exist = User.query.filter_by(user_id=user_id).first()
        if not user_exist:
            abort(HTTPStatus.NOT_FOUND, message='This user does not exist')
        else:
            return user_exist, HTTPStatus.OK
