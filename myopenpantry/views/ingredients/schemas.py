import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.ingredients import Ingredient
from myopenpantry.models import RecipeIngredient


class IngredientSchema(AutoSchema):
    id = field_for(Ingredient, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Ingredient.__table__


class IngredientQueryArgsSchema(Schema):
    name = ma.fields.Str(validate=ma.validate.Length(min=1))


class IngredientItemsSchema(Schema):
    item_id = ma.fields.Int(strict=True, validate=ma.validate.Range(min=1), required=True)


# used to nest to make bulk recipe/ingredient associations
class IngredientRecipesSchema(Schema):
    # don't allow the user to accidentally (or purposefully) change the recipe id
    ingredient_id = field_for(RecipeIngredient, 'ingredient_id', dump_only=True, validate=ma.validate.Range(min=1))

    recipe_id = ma.fields.Int(required=True, strict=True, validate=ma.validate.Range(min=1))
    # TODO Decimal gives an error
    amount = ma.fields.Float(required=True, strict=True, validate=ma.validate.Range())
    unit = ma.fields.Str(required=True, validate=ma.validate.Length(min=1))


# TODO better name for this?
class BulkIngredientRecipesSchema(Schema):
    recipe_ingredients = ma.fields.List(
        ma.fields.Nested(IngredientRecipesSchema),
        validate=ma.validate.Length(min=1),
    )
