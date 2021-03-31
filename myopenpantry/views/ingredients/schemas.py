import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.ingredients import Ingredient

class IngredientSchema(AutoSchema):
    id = field_for(Ingredient, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Ingredient.__table__

class IngredientQueryArgsSchema(Schema):
    name = ma.fields.Str()
    recipe_id = ma.fields.Int()
    item_id = ma.fields.Int()
