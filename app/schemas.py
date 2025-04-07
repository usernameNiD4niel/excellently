from app import ma
from app.models import Item

class ItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Item

    id = ma.auto_field()
    name = ma.auto_field()
    created_at = ma.auto_field()
    updated_at = ma.auto_field()

item_schema = ItemSchema()
items_schema = ItemSchema(many=True) 