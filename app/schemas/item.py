from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.item import Item

class ItemSchema(SQLAlchemySchema):
    class Meta:
        model = Item
        load_instance = True
        include_relationships = True

    id = auto_field(dump_only=True)
    name = auto_field(required=True, validate=validate.Length(min=1, max=100))
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

# Create schema instances
item_schema = ItemSchema()
items_schema = ItemSchema(many=True) 