from flask.views import MethodView
from flask_smorest import abort

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient, Tag, RecipeIngredient

from sqlalchemy import and_, exc

from .schemas import (
    RecipeSchema, RecipeQueryArgsSchema, RecipeTagSchema,
    BulkRecipeIngredientSchema, RecipeIngredientSchema
)
from ..tags.schemas import TagSchema

blp = Blueprint(
    'Recipes',
    __name__,
    url_prefix='/recipes',
    description="Operations on recipes"
)


# TODO this is duplicated in each view. Create a controller to move all backend logic to
# Trying to stay consistent with other error stuctures, eg:
# "errors": {
#   "json": {
#     "ingredientId": [
#       "Must be greater than or equal to 0."
#     ]
#   }
# }, which is returned when by the Schema validation
def handle_integrity_error_and_abort(e):
    # TODO surely there is a better way to figure out what the error type is?
    # TODO log the error
    e = repr(e)
    errors = {'json': {}}
    if e.find('UNIQUE constraint failed: recipes.name') != -1:
        errors['json']['name'] = ["Recipe with that name already exists"]

    abort(422, errors=errors)


@blp.route('/')
class Recipes(MethodView):

    @blp.etag
    @blp.arguments(RecipeQueryArgsSchema, location='query')
    @blp.response(200, RecipeSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List all recipes or filter by args"""
        name = args.pop('name', None)

        ret = Recipe.query.filter_by(**args)

        # TODO does marshmallow have a way to only allow one of these at a time?
        if name is not None:
            ret = ret.filter(Recipe.name.like(f"%{name}%"))

        return ret.order_by(Recipe.id)

    @blp.etag
    @blp.arguments(RecipeSchema)
    @blp.response(201, RecipeSchema)
    def post(self, new_recipe):
        """Add a new recipe"""
        recipe = Recipe(**new_recipe)

        try:
            db.session.add(recipe)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")

        return recipe


@blp.route('/<int:recipe_id>')
class RecipesbyID(MethodView):

    @blp.etag
    @blp.response(200, RecipeSchema)
    def get(self, recipe_id):
        """Get recipe by ID"""
        return Recipe.query.get_or_404(recipe_id)

    @blp.etag
    @blp.arguments(RecipeSchema)
    @blp.response(200, RecipeSchema)
    def put(self, new_recipe, recipe_id):
        """Update an existing recipe"""
        recipe = Recipe.query.get_or_404(recipe_id)

        blp.check_etag(recipe, RecipeSchema)

        RecipeSchema().update(recipe, new_recipe)

        try:
            db.session.add(recipe)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")

        return recipe

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id):
        """Delete a recipe"""
        recipe = Recipe.query.get_or_404(recipe_id)

        blp.check_etag(recipe, RecipeSchema)

        try:
            db.session.delete(recipe)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)


@blp.route('/<int:recipe_id>/tags')
class RecipeTags(MethodView):

    @blp.etag
    @blp.response(200, TagSchema(many=True))
    def get(self, recipe_id):
        """Get tags associated with a recipe"""
        return Recipe.query.get_or_404(recipe_id).tags

    @blp.etag
    @blp.arguments(RecipeTagSchema)
    @blp.response(204)
    def post(self, args, recipe_id):
        """Add association between a recipe and tag"""
        recipe = Recipe.query.get_or_404(recipe_id)

        # tag_ids are required by the schema, so shouldn't need to check if they are none
        tag_ids = args.pop('tag_ids', None)
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)

            if tag is None:
                abort(422)

            recipe.tags.append(tag)

        try:
            db.session.add(recipe)
            db.session.commit()
        except (exc.IntegrityError, exc.DatabaseError):
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")


@blp.route('/<int:recipe_id>/tags/<int:tag_id>')
class RecipeTagsDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id, tag_id):
        """Delete association between a recipe and tag"""
        recipe = Recipe.query.get_or_404(recipe_id)
        tag = Tag.query.with_parent(recipe).filter(Tag.id == tag_id).first()

        if tag is None:
            abort(422)

        blp.check_etag(recipe, RecipeSchema)

        recipe.tags.remove(tag)

        try:
            db.session.add(recipe)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)


@blp.route('/<int:recipe_id>/ingredients')
class RecipeIngredients(MethodView):

    @blp.etag
    @blp.response(200, RecipeIngredientSchema(many=True))
    def get(self, recipe_id):
        """Get ingredients associated with a recipe"""
        return Recipe.query.get_or_404(recipe_id).ingredients

    @blp.etag
    @blp.arguments(BulkRecipeIngredientSchema)
    @blp.response(204)
    def post(self, args, recipe_id):
        """Add association between a recipe and ingredient"""
        recipe = Recipe.query.get_or_404(recipe_id)

        recipe_ingredients = args.pop('recipe_ingredients', None)
        for recipe_ingredient in recipe_ingredients:
            ingredient = Ingredient.query.get(recipe_ingredient['ingredient_id'])

            if ingredient is None:
                abort(422)

            association = RecipeIngredient(amount=recipe_ingredient['amount'], unit=recipe_ingredient['unit'])
            association.ingredient_id = ingredient.id
            association.ingredient = ingredient
            association.recipe_id = recipe_id
            association.recipe = recipe

            ingredient.recipes.append(association)
            recipe.ingredients.append(association)

        try:
            db.session.add(ingredient)
            db.session.add(recipe)
            db.session.add(association)
            db.session.commit()
        except (exc.IntegrityError, exc.DatabaseError):
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")


@blp.route('/<int:recipe_id>/ingredients/<int:ingredient_id>')
class RecipeIngredientsDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id, ingredient_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id) # noqa
        recipe = Recipe.query.get_or_404(recipe_id)

        # TODO would a join be better here?
        association = RecipeIngredient.query.filter(
            and_(RecipeIngredient.recipe_id == recipe_id, RecipeIngredient.ingredient_id == ingredient_id)
        ).first()

        if association is None:
            abort(422)

        blp.check_etag(recipe, RecipeSchema)

        try:
            db.session.delete(association)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)
