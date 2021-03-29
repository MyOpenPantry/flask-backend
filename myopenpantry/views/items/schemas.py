import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.items import Item

class ItemSchema(AutoSchema):
    id = field_for(Item, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Item.__table__

class ItemQueryArgsSchema(Schema):
    name = ma.fields.Str()
    product_id = ma.fields.Int()
    ingredient_id = ma.fields.Int()
