import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.items import Item

class ItemSchema(AutoSchema):
    id = field_for(Item, "id", dump_only=True)
    updated_at = field_for(Item, "updated_at", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Item.__table__

class ItemQueryArgsSchema(Schema):
    names = ma.fields.List(ma.fields.Str(validate=ma.validate.Length(min=1)))
    product_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)))
    ingredient_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)))
