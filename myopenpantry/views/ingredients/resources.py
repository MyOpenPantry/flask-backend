from flask.views import MethodView
from flask_smorest import abort

from sqlalchemy import or_

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient, Item, RecipeIngredient

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
        recipe_ids = args.pop('recipe_ids', None)
        item_ids = args.pop('item_ids', None)
        names = args.pop('names', None)

        ret = Ingredient.query.filter_by(**args)

        # TODO is filtering by recipe_id and item_id redundant when items/{id}/ingredient and recipes/{id}/ingredients exists?

        # TODO does marshmallow have a way to only allow one of these at a time?
        # recipe_id > item_id > name for search order
        if recipe_ids is not None:
            #ret = ret.join(RecipeIngredient, Recipe.ingredients).filter(or_(RecipeIngredient.ingredient_id == id for id in ingredient_ids))
            
            ret = ret.join(RecipeIngredient, Ingredient.recipes).filter(or_(RecipeIngredient.recipe_id == id for id in recipe_ids))
        elif item_ids is not None:
            ret = ret.join(Item, Ingredient.items).filter(or_(Item.id == id for id in item_ids))
        elif names is not None:
            ret = ret.filter(or_(Ingredient.name.like(f"%{name}%") for name in names))

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
    def post(self, args, ingredient_id):
        """Add association between a recipe and ingredient"""
        ingredient = Ingredient.get_or_404(ingredient_id)

        recipe_id = args.pop('recipe_id', None)
        recipe = Recipe.query.get(recipe_id)

        if recipe is None:
            abort(422)

        ingredient.recipes.append(recipe)

        try:
            db.session.add(ingredient)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

@blp.route('/<int:ingredient_id>/recipes/<int:recipe_id>')
class IngredientRecipesDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, ingredient_id, recipe_id):
        """Delete association between a recipe and ingredient"""
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        recipe = Recipe.query.with_parent(ingredient).filter(Recipe.id == recipe_id).first()

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
        except:
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
        except:
            db.session.rollback()
            abort(422)
