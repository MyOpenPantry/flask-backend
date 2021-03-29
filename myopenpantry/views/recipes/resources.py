from flask.views import MethodView

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Tag

from .schemas import RecipeSchema, RecipeQueryArgsSchema

blp = Blueprint(
    'Recipes',
    __name__,
    url_prefix='/recipes',
    description="Operations on recipes"
)

@blp.route('/')
class Recipes(MethodView):

    @blp.etag
    @blp.arguments(RecipeQueryArgsSchema, location='query')
    @blp.response(200, RecipeSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List recipes"""
        tag_id = args.pop('tag_id', None)
        ret = Recipe.query.filter_by(**args)
        if tag_id is not None:
            ret = ret.join(Recipe.tags).filter(Tag.id == tag_id)
        return ret

    @blp.etag
    @blp.arguments(RecipeSchema)
    @blp.response(201, RecipeSchema)
    def post(self, new_item):
        """Add a new recipe"""
        recipe = Recipe(**new_item)
        db.session.add(recipe)
        db.session.commit()
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
        """Update an existing member"""
        recipe = Recipe.query.get_or_404(recipe_id)
        blp.check_etag(recipe, RecipeSchema)
        RecipeSchema().update(recipe, new_recipe)
        db.session.add(recipe)
        db.session.commit()
        return recipe

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id):
        """Delete a recipe"""
        recipe = Member.query.get_or_404(recipe_id)
        blp.check_etag(recipe, RecipeSchema)
        db.session.delete(recipe)
        db.session.commit()
