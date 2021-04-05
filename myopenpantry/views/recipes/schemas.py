import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.recipes import Recipe

class RecipeSchema(AutoSchema):
    id = field_for(Recipe, "id", dump_only=True)
    created_at = field_for(Recipe, "created_at", dump_only=True)
    updated_at = field_for(Recipe, "updated_at", dump_only=True)
    rating = field_for(Recipe, 'rating', validate=ma.validate.Range(min=0))

    class Meta(AutoSchema.Meta):
        table = Recipe.__table__

class RecipeQueryArgsSchema(Schema):
    names = ma.fields.List(ma.fields.Str(validate=ma.validate.Length(min=1)))
    tag_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)))
    ingredient_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)))

class RecipeTagSchema(Schema):
    tag_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)), required=True)

class RecipeIngredientSchema(Schema):
    ingredient_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)), required=True)