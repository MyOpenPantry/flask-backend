from flask.views import MethodView
from flask_smorest import abort

from sqlalchemy import and_, exc

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient, Item, RecipeIngredient

from .schemas import (
    IngredientSchema, IngredientQueryArgsSchema, IngredientItemsSchema,
    BulkIngredientRecipesSchema, IngredientRecipesSchema
)
from ..items.schemas import ItemSchema

blp = Blueprint(
    'Ingredients',
    __name__,
    url_prefix='/ingredients',
    description="Operations on ingredients"
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
    if e.find('UNIQUE constraint failed: items.name') != -1:
        errors['json']['name'] = ["Item with that name already exists"]
    elif e.find('UNIQUE constraint failed: items.product_id') != -1:
        errors['json']['productId'] = ["Item with that product ID already exists"]
    elif e.find('FOREIGN KEY constraint failed') != -1:
        errors['json']['ingredientId'] = ["No such ingredient with that id"]

    abort(422, errors=errors)


@blp.route('/')
class Ingredients(MethodView):

    @blp.etag
    @blp.arguments(IngredientQueryArgsSchema, location='query')
    @blp.response(200, IngredientSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List all ingredients or filter by args"""
        name = args.pop('name', None)

        ret = Ingredient.query.filter_by(**args)

        if name is not None:
            ret = ret.filter(Ingredient.name.like(f"%{name}%"))

        return ret.order_by(Ingredient.id)

    @blp.etag
    @blp.arguments(IngredientSchema)
    @blp.response(201, IngredientSchema)
    def post(self, new_item):
        """Add a new ingredient"""
        ingredient = Ingredient(**new_item)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")
        return ingredient


@blp.route('/<int:ingredient_id>')
class IngredientsById(MethodView):

    @blp.etag
    @blp.response(200, IngredientSchema)
    def get(self, ingredient_id):
        """Get ingredient by ID"""
        return Ingredient.query.get_or_404(ingredient_id)

    @blp.etag
    @blp.arguments(IngredientSchema)
    @blp.response(200, IngredientSchema)
    def put(self, new_ingredient, ingredient_id):
        """Update an existing ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        blp.check_etag(ingredient, IngredientSchema)

        IngredientSchema().update(ingredient, new_ingredient)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")
        return ingredient

    @blp.etag
    @blp.response(204)
    def delete(self, ingredient_id):
        """Delete an ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        blp.check_etag(ingredient, IngredientSchema)

        try:
            db.session.delete(ingredient)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)


@blp.route('/<int:ingredient_id>/recipes')
class IngredientRecipes(MethodView):

    @blp.etag
    @blp.response(200, IngredientRecipesSchema(many=True))
    def get(self, ingredient_id):
        """Get recipes associated with the ingredient"""
        return Ingredient.query.get_or_404(ingredient_id).recipes

    @blp.etag
    @blp.arguments(BulkIngredientRecipesSchema)
    @blp.response(204)
    def post(self, args, ingredient_id):
        """Add association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        recipe_ingredients = args.pop('recipe_ingredients', None)
        for recipe_ingredient in recipe_ingredients:
            # use .get() instead of .get_or_404(),
            # because we want to return 422 if recipe_id doesn't exist since recipe_id is not passed in the URL
            recipe = Recipe.query.get(recipe_ingredient['recipe_id'])

            if recipe is None:
                abort(422)

            association = RecipeIngredient(amount=recipe_ingredient['amount'], unit=recipe_ingredient['unit'])
            association.ingredient_id = ingredient_id
            association.ingredient = ingredient
            association.recipe_id = recipe.id
            association.recipe = recipe

            ingredient.recipes.append(association)
            recipe.ingredients.append(association)

        try:
            db.session.add(ingredient)
            db.session.add(recipe)
            db.session.add(association)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)


@blp.route('/<int:ingredient_id>/recipes/<int:recipe_id>')
class IngredientRecipesDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, ingredient_id, recipe_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        recipe = Recipe.query.get_or_404(recipe_id) # noqa

        # TODO would a join be better here?
        association = RecipeIngredient.query.filter(
            and_(RecipeIngredient.recipe_id == recipe_id, RecipeIngredient.ingredient_id == ingredient_id)
        ).first()

        if association is None:
            abort(422)

        blp.check_etag(ingredient, IngredientSchema)

        db.session.delete(association)
        db.session.commit()


@blp.route('/<int:ingredient_id>/items')
class IngredientItems(MethodView):

    @blp.etag
    @blp.response(200, ItemSchema(many=True))
    def get(self, ingredient_id):
        """Get items associated with the ingredient"""
        return Ingredient.query.get_or_404(ingredient_id).items

    @blp.etag
    @blp.arguments(IngredientItemsSchema)
    @blp.response(204)
    def post(self, args, ingredient_id):
        """Add association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        item_id = args.pop('item_id', None)
        item = Item.query.get(item_id)

        if item is None:
            abort(422)

        ingredient.items.append(item)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)


@blp.route('/<int:ingredient_id>/items/<int:item_id>')
class IngredientItemsDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, ingredient_id, item_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        item = Item.query.with_parent(ingredient).filter(Item.id == item_id).first()

        if item is None:
            abort(422)

        blp.check_etag(ingredient, IngredientSchema)

        ingredient.items.remove(item)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.DatabaseError:
            db.session.rollback()
            abort(422)
