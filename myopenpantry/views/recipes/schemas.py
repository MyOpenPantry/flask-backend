import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.recipes import Recipe
from myopenpantry.models.associations import RecipeIngredient

class RecipeSchema(AutoSchema):
    id = field_for(Recipe, "id", dump_only=True)
    created_at = field_for(Recipe, "created_at", dump_only=True)
    updated_at = field_for(Recipe, "updated_at", dump_only=True)
    rating = field_for(Recipe, 'rating', validate=ma.validate.Range(min=0))

    class Meta(AutoSchema.Meta):
        table = Recipe.__table__

class RecipeQueryArgsSchema(Schema):
    names = ma.fields.List(ma.fields.Str(validate=ma.validate.Length(min=1)), validate=ma.validate.Length(min=1))
    tag_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)), validate=ma.validate.Length(min=1))
    ingredient_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)), validate=ma.validate.Length(min=1))

class RecipeTagSchema(Schema):
    tag_ids = ma.fields.List(
        ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)),
        required=True, validate=ma.validate.Length(min=1)
    )

# used to nest to make bulk recipe/ingredient associations
class RecipeIngredientSchema(AutoSchema):
    # don't allow the user to accidentally (or purposefully) change the recipe id
    recipe_id = field_for(RecipeIngredient, 'recipe_id', dump_only=True, validate=ma.validate.Range(min=1))

    ingredient_id = ma.fields.Int(required=True, strict=True, validate=ma.validate.Range(min=1))
    amount = ma.fields.Decimal(required=True, strict=True, validate=ma.validate.Range(min=0.0))
    unit = ma.fields.Str(required=True, validate=ma.validate.Length(min=1))

# TODO better name for this?
class BulkRecipeIngredientSchema(Schema):
    recipe_ingredients = ma.fields.List(ma.fields.Nested(RecipeIngredientSchema), validate=ma.validate.Length(min=1))
