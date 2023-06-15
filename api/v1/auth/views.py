from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..models.users import User
from ..models.schemas import UserSchema, LinkSchema, ViewCountSchema, ViewLogSchema
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash


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
        if email_exist:
            abort(HTTPStatus.NOT_ACCEPTABLE, message='This email already exists')
        else:
            new_user = User(
                username=new_data['username'],
                firstname=new_data['firstname'],
                lastname=new_data['lastname'],
                email=new_data['email'],
                password_hash=generate_password_hash(new_data['password']),
            )
            new_user.save()

        return new_user, HTTPStatus.CREATED
