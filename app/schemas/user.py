from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.user import User

class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = True

    id = auto_field(dump_only=True)
    email = auto_field(required=True, validate=validate.Email())
    username = auto_field(required=True, validate=validate.Length(min=3, max=50))
    name = auto_field(required=True, validate=validate.Length(min=2, max=100))
    is_active = auto_field(dump_only=True)
    is_premium = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    last_login = auto_field(dump_only=True)

class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

# Create schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema() 