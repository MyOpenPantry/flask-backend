import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.ingredients import Ingredient

class IngredientSchema(AutoSchema):
    id = field_for(Ingredient, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Ingredient.__table__

class IngredientQueryArgsSchema(Schema):
    names = ma.fields.List(
        ma.fields.Str(validate=ma.validate.Length(min=1)),
        validate=ma.validate.Length(min=1)
    )
    recipe_ids = ma.fields.List(
        ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)),
        validate=ma.validate.Length(min=1)
    )
    item_ids = ma.fields.List(
        ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)),
        validate=ma.validate.Length(min=1)
    )

class IngredientItemsSchema(Schema):
    item_id = ma.fields.Int(strict=True, validate=ma.validate.Range(min=1), required=True)

class IngredientRecipesSchema(Schema):
    recipe_id = ma.fields.Int(strict=True, validate=ma.validate.Range(min=1), required=True)
