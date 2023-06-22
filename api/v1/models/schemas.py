from marshmallow import RAISE
from marshmallow.validate import Length, Email
from marshmallow_sqlalchemy import field_for
from ..models.users import User
from ..models.links import Link
from ..models.view_counts import ViewCount
from ..models.view_logs import ViewLog
from api.v1 import ma


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True
        unknown = RAISE

    user_id = field_for(User, "user_id", dump_only=True)
    username = field_for(User, "username", required=True, validate=Length(min=2, max=45))
    firstname = field_for(User, "firstname", required=True, validate=Length(min=2, max=45))
    lastname = field_for(User, "lastname", required=True, validate=Length(min=2, max=45))
    email = field_for(User, "email", required=True, validate=[Length(min=5, max=50), Email()])
    password = field_for(User, "password_hash", required=True, load_only=True)


LoginArgSchema = UserSchema(partial=('email', 'username', 'firstname', 'lastname',))
LoginResponseSchema = UserSchema(exclude=('firstname', 'lastname',))


class LinkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Link
        ordered = True
        unknown = RAISE

    link_id = field_for(Link, "link_id", dump_only=True)
    user_id = field_for(Link, "user_id", load_only=True)
    true_link = field_for(Link, "true_link", required=True, validate=Length(min=2, max=45))
    custom_link = field_for(Link, "custom_link", required=True, validate=Length(min=2, max=32))
    short_link = field_for(Link, "short_link", required=True, validate=Length(min=2, max=45))
    created_on = field_for(Link, "created_on", load_only=True, validate=[Length(min=5, max=50), Email()])


LinkArgSchema = LinkSchema(partial=('custom_link', 'short_link'))
CustomArgSchema = LinkSchema(partial=('short_link'))


class ViewCountSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ViewCount
        ordered = True
        unknown = RAISE

    link_id = field_for(ViewCount, "link_id", dump_only=True)
    view_count = field_for(ViewCount, "view_count", dump_only=True)


class ViewLogSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ViewLog
        ordered = True
        unknown = RAISE

    view_log_id = field_for(ViewLog, "view_log_id", dump_only=True)
    short_link = field_for(ViewLog, "short_link", dump_only=True)
    ip_address = field_for(ViewLog, "ip_address", dump_only=True)
    viewed_on = field_for(ViewLog, "viewed_on", dump_only=True)
