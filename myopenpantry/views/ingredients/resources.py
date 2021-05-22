from flask.views import MethodView
from flask_smorest import abort

from sqlalchemy import exc

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Ingredient

from .schemas import IngredientSchema, IngredientQueryArgsSchema
import myopenpantry.views.recipes.schemas as RS
import myopenpantry.views.items.schemas as IS

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
    if e.find('UNIQUE constraint failed: ingredients.name') != -1:
        errors['json']['name'] = ["Ingredient with that name already exists"]

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
    @blp.response(200, RS.RecipeSchema(many=True))
    def get(self, ingredient_id):
        """Get recipes associated with the ingredient"""
        return Ingredient.query.get_or_404(ingredient_id).recipes


@blp.route('/<int:ingredient_id>/items')
class IngredientItems(MethodView):

    @blp.etag
    @blp.response(200, IS.ItemSchema(many=True))
    def get(self, ingredient_id):
        """Get items associated with the ingredient"""
        return Ingredient.query.get_or_404(ingredient_id).items
