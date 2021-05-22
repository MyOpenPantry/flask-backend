import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.items import Item

from myopenpantry.views.ingredients.schemas import IngredientSchema


class ItemSchema(AutoSchema):
    id = field_for(Item, "id", dump_only=True)
    name = field_for(Item, "name", validate=ma.validate.Length(min=1))
    amount = field_for(Item, "amount", validate=ma.validate.Range(min=0))
    updated_at = field_for(Item, "updated_at", dump_only=True)
    # product ids can be a max of 13 digits
    product_id = field_for(Item, 'product_id', validate=ma.validate.Range(min=1, max=9999999999999))

    # ingredient_id is write only, the ingredient schema will be returned instead if ingredient_id is set
    ingredient_id = field_for(Item, 'ingredient_id', validate=ma.validate.Range(min=0), load_only=True)
    ingredient = ma.fields.Nested(IngredientSchema)

    class Meta(AutoSchema.Meta):
        table = Item.__table__


class ItemQueryArgsSchema(Schema):
    name = ma.fields.Str(validate=ma.validate.Length(min=1))
    product_id = ma.fields.Int(validate=ma.validate.Range(min=1, max=9999999999999))
