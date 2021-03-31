import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.recipes import Recipe

class RecipeSchema(AutoSchema):
    id = field_for(Recipe, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Recipe.__table__

class RecipeQueryArgsSchema(Schema):
    name = ma.fields.Str()
    tag_id = ma.fields.Int()
    ingredient_id = ma.fields.Int()
