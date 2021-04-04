from flask.views import MethodView
from flask_smorest import abort

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe

from sqlalchemy import or_

from .schemas import RecipeSchema, RecipeQueryArgsSchema
from ..tags.schemas import TagSchema
from ..ingredients.schemas import IngredientSchema

blp = Blueprint(
    'Recipes',
    __name__,
    url_prefix='/recipes',
    description="Operations on recipes"
)

@blp.route('/')
class Recipes(MethodView):

    @blp.etag
    @blp.arguments(RecipeQueryArgsSchema)
    @blp.response(200, RecipeSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List recipes"""
        ingredient_ids = args.pop('ingredient_ids', None)
        tag_ids = args.pop('tag_ids', None)
        names = args.pop('names', None)

        ret = Recipe.query.filter_by(**args)

        # TODO does marshmallow have a way to only allow one of these at a time?
        if ingredient_ids is not None:
            ret = ret.filter(Recipe.ingredients.in_(ingredient_ids))
        elif tag_ids is not None:
            ret = ret.filter(Recipe.tags.id.in_(tag_ids))
        elif names is not None:
            ret = ret.filter(or_(Recipe.name.like(f"%{name}%") for name in names))

        return ret

    @blp.etag
    @blp.arguments(RecipeSchema)
    @blp.response(201, RecipeSchema)
    def post(self, new_recipe):
        """Add a new recipe"""
        recipe = Recipe(**new_recipe)

        try:
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

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
        except:
            db.session.rollback()
            abort(422)

        return recipe

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id):
        """Delete a recipe"""
        recipe = Recipe.query.get_or_404(recipe_id)

        blp.check_etag(recipe, RecipeSchema)

        db.session.delete(recipe)
        db.session.commit()

@blp.route('/<int:recipe_id>/tags')
class RecipeTags(MethodView):

    @blp.etag
    @blp.response(200, TagSchema(many=True))
    def get(self, recipe_id):
        """Get tags associated with a recipe"""
        return Recipe.query.get_or_404(recipe_id).tags

@blp.route('/<int:recipe_id>/tags/<int:tag_id>')
class RecipeTagsOps(MethodView):

    @blp.etag
    @blp.response(204)
    def put(self, recipe_id, tag_id):
        """Add association between a recipe and tag"""
        recipe = Recipe.query.get_or_404(recipe_id)
        tag = Tag.query.get_or_404(tag_id)

        blp.check_etag(recipe, RecipeSchema)

        recipe.tags.add(tag)

        try:
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)


    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id, tag_id):
        """Delete association between a recipe and tag"""
        recipe = Recipe.query.get_or_404(recipe_id)
        tag = recipe.tags.get_or_404(tag_id)

        blp.check_etag(recipe, RecipeSchema)

        recipe.tags.remove(tag)

        try:
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)


@blp.route('/<int:recipe_id>/ingredients')
class RecipeIngredients(MethodView):

    @blp.etag
    @blp.response(200, IngredientSchema(many=True))
    def get(self, recipe_id):
        """Get ingredients associated with a recipe"""
        return Recipe.query.get_or_404(recipe_id).ingredients

@blp.route('/<int:recipe_id>/tags/<int:ingredient_id>')
class RecipeIngredientsOps(MethodView):

    @blp.etag
    @blp.response(204)
    def put(self, recipe_id, ingredient_id):
        """Add association between a recipe and ingredient"""
        recipe = Recipe.query.get_or_404(recipe_id)
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        blp.check_etag(recipe, RecipeSchema)

        recipe.ingredients.add(ingredient)

        try:
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id, ingredient_id):
        """Delete association between a recipe and ingredient"""
        recipe = Recipe.query.get_or_404(recipe_id)
        ingredient = recipe.ingredients.get_or_404(ingredient_id)

        blp.check_etag(recipe, RecipeSchema)

        recipe.ingredients.remove(ingredient)

        try:
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
