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
        """Add a new recipe"""
        ingredient = Ingredient(**new_item)
        db.session.add(ingredient)
        db.session.commit()
        return ingredient
