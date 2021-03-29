from flask.views import MethodView

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient

from .schemas import IngredientSchema, IngredientQueryArgsSchema

blp = Blueprint(
    'Ingredients',
    __name__,
    url_prefix='/ingredients',
    description="Operations on ingredients"
)

@blp.route('/')
class Ingredients(MethodView):

    @blp.etag
    @blp.arguments(IngredientQueryArgsSchema, location='query')
    @blp.response(200, IngredientSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List ingredients"""
        recipe_id = args.pop('recipe_id', None)
        ret = Ingredient.query.filter_by(**args)
        if recipe_id is not None:
            ret = ret.join(Ingredient.recipes).filter(Recipe.id == recipe_id)
        return ret

    @blp.etag
    @blp.arguments(IngredientSchema)
    @blp.response(201, IngredientSchema)
    def post(self, new_item):
        """Add a new ingredient"""
        ingredient = Ingredient(**new_item)
        db.session.add(ingredient)
        db.session.commit()
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
        db.session.add(ingredient)
        db.session.commit()
        return ingredient

    @blp.etag
    @blp.response(204)
    def delete(self, ingredient_id):
        """Delete an ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        blp.check_etag(ingredient, IngredientSchema)
        db.session.delete(ingredient)
        db.session.commit()
