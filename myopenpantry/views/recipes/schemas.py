import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.recipes import Recipe
from myopenpantry.models.tags import Tag
from myopenpantry.models.associations import RecipeIngredient
from myopenpantry.views.ingredients.schemas import IngredientSchema


# Due to circular dependencies, define tags here since they are only useful with recipes anyway
class TagSchema(AutoSchema):
    id = field_for(Tag, "id", dump_only=True)
    name = field_for(Tag, 'name', validate=ma.validate.Length(min=1))

    class Meta(AutoSchema.Meta):
        table = Tag.__table__


class TagQueryArgsSchema(Schema):
    name = ma.fields.Str(validate=ma.validate.Length(min=1))


# used to nest to make bulk recipe/ingredient associations
class RecipeIngredientSchema(AutoSchema):
    # don't allow the user to accidentally (or purposefully) change the recipe id
    # recipe_id = field_for(RecipeIngredient, 'recipe_id', dump_only=True, validate=ma.validate.Range(min=1))
    amount = ma.fields.Float(required=True, validate=ma.validate.Range(min=0.0))
    unit = ma.fields.Str(required=True, validate=ma.validate.Length(min=1))

    # ingredient_id is write only, the ingredient schema will be returned on GET
    ingredient_id = ma.fields.Integer(validate=ma.validate.Range(min=0), load_only=True)
    ingredient = ma.fields.Nested(IngredientSchema, dump_only=True)

    recipe_id = field_for(RecipeIngredient, 'recipe_id', dump_only=True)

    class Meta(AutoSchema.Meta):
        table = RecipeIngredient.__table__


class RecipeSchema(AutoSchema):
    id = field_for(Recipe, "id", dump_only=True)
    created_at = field_for(Recipe, "created_at", dump_only=True)
    updated_at = field_for(Recipe, "updated_at", dump_only=True)
    rating = field_for(Recipe, 'rating', validate=ma.validate.Range(min=0))

    ingredients = ma.fields.Nested(RecipeIngredientSchema, many=True)

    # only used on POST to add tags to the recipe
    tag_ids = ma.fields.List(ma.fields.Integer(validate=ma.validate.Range(min=1), load_only=True))
    tags = ma.fields.Nested(TagSchema, many=True, dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Recipe.__table__


class RecipeQueryArgsSchema(Schema):
    name = ma.fields.Str(validate=ma.validate.Length(min=1))
