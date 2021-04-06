from flask.views import MethodView
from flask_smorest import abort

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient, Item

from .schemas import IngredientSchema, IngredientQueryArgsSchema, IngredientItemsSchema, IngredientRecipesSchema
from ..items.schemas import ItemSchema
from ..recipes.schemas import RecipeSchema 

blp = Blueprint(
    'Ingredients',
    __name__,
    url_prefix='/ingredients',
    description="Operations on ingredients"
)

@blp.route('/')
class Ingredients(MethodView):

    @blp.etag
    @blp.arguments(IngredientQueryArgsSchema)
    @blp.response(200, IngredientSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List all ingredients or filter by args"""
        recipe_id = args.pop('recipe_id', None)
        item_id = args.pop('item_id', None)
        name = args.pop('name', None)

        ret = Ingredient.query.filter_by(**args)

        # TODO is filtering by recipe_id and item_id redundant when items/{id}/ingredient and recipes/{id}/ingredients exists?

        # TODO does marshmallow have a way to only allow one of these at a time?
        # recipe_id > item_id > name for search order
        if recipe_id is not None:
            ret = ret.filter(recipe_id in Ingredient.recipes)
        elif item_id is not None:
            ret = ret.filter(item_id in Ingredient.items)
        elif name is not None:
            name = f"%{name}%"
            ret = ret.filter(Ingredient.name.like(name))

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
        except:
            db.session.rollback()
            # TODO be more descriptive and log
            abort(422)
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
        except:
            db.session.rollback()
            # TODO be more descriptive and log
            abort(422)
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
        except:
            db.session.rollback()
            abort(422)


@blp.route('/<int:ingredient_id>/recipes')
class IngredientRecipes(MethodView):

    @blp.etag
    @blp.response(200, RecipeSchema(many=True))
    def get(self, ingredient_id):
        """Get recipes associated with the ingredient"""
        return Ingredient.query.get_or_404(ingredient_id).recipes

    @blp.etag
    @blp.arguments(IngredientRecipesSchema)
    @blp.response(204)
    def post(self, ingredient_id):
        """Add association between a recipe and ingredient"""
        ingredient = Ingredient.get_or_404(ingredient_id)

        recipe_id = args.pop('recipe_id', None)
        recipe = Recipe.query.get_or_404(recipe_id)

        ingredient.recipes.add(recipe)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

@blp.route('/<int:ingredient_id>/recipes/<int:recipe_id>')
class IngredientRecipesDelete(MethodView):

    @blp.etag
    @blp.arguments(IngredientRecipesSchema)
    @blp.response(204)
    def delete(self, ingredient_id, recipe_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        recipe = ingredient.recipes.filter(Recipe.id == recipe_id).first()

        if recipe is None:
            abort(404)

        blp.check_etag(ingredient, IngredientSchema)

        ingredient.recipes.remove(recipe)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

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
    def post(self, ingredient_id):
        """Add association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)

        item_id = args.pop('item_id', None)
        item = Item.query.get_or_404(item_id)

        ingredient.recipes.add(item)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

@blp.route('/<int:ingredient_id>/items/<int:item_id>')
class IngredientItemsDelete(MethodView):

    @blp.etag
    @blp.arguments(IngredientItemsSchema)
    @blp.response(204)
    def delete(self, ingredient_id, item_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        item = ingredient.items.filter(Item.id == item_id).first()

        if item is None:
            abort(404)

        blp.check_etag(ingredient, IngredientSchema)

        ingredient.recipes.remove(item)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
