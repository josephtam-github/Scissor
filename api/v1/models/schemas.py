from marshmallow import EXCLUDE
from marshmallow.validate import Length, Email
from marshmallow_sqlalchemy import field_for
from ..models.users import User
from api.v1 import ma


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True
        unknown = EXCLUDE

    user_id = field_for(User, "user_id", dump_only=True)
    username = field_for(User, "username", required=True, validate=Length(min=2, max=45))
    firstname = field_for(User, "firstname", required=True, validate=Length(min=2, max=45))
    lastname = field_for(User, "lastname", required=True, validate=Length(min=2, max=45))
    email = field_for(User, "email", required=True, validate=[Length(min=5, max=50), Email()])