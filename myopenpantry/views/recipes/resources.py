from flask.views import MethodView
from flask_smorest import abort

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Recipe, Ingredient, Tag, RecipeIngredient

from sqlalchemy import and_, exc

from .schemas import RecipeSchema, RecipeQueryArgsSchema, RIngredientSchema, TagSchema, RecipeTagSchema

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
        can_make = args.pop('can_make', False)

        ret = Recipe.query.filter_by(**args)

        # TODO does marshmallow have a way to only allow one of these at a time?
        if name is not None:
            ret = ret.filter(Recipe.name.like(f"%{name}%"))

        # TODO this doesn't check to see that the amount is enough to make the recipe,
        # which will be difficult given that the units are user defined
        if can_make:
            # TODO do this with SQL. Need to brush up on how to accomplish this
            # I can get the number of ingredients a recipe has, and the ingredients with items with amount > 0,
            # but am having issues connecting all the dots...
            cant_make = []
            for recipe in ret.all():
                has_all = True
                for ring in recipe.ingredients:
                    if (len(ring.ingredient.items) == 0) or not any(item.amount > 0 for item in ring.ingredient.items):
                        has_all = False
                        break

                if not has_all:
                    cant_make.append(recipe.id)

            ret = ret.filter(~Recipe.id.in_(cant_make))

        return ret.order_by(Recipe.id)

    @blp.etag
    @blp.arguments(RecipeSchema)
    @blp.response(201, RecipeSchema)
    def post(self, new_recipe):
        """Add a new recipe"""
        # tag_ids are required by the schema, so shouldn't need to check if they are none
        ingredients = new_recipe.pop('ingredients', None)

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

        if ingredients is not None:
            for ringredient in ingredients:
                ingredient = Ingredient.query.get(ringredient['ingredient_id'])

                if ingredient is None:
                    abort(422)

                association = RecipeIngredient(amount=ringredient['amount'], unit=ringredient['unit'])
                association.ingredient_id = ingredient.id
                association.ingredient = ingredient
                association.recipe_id = recipe.id
                association.recipe = recipe

                ingredient.recipes.append(association)
                recipe.ingredients.append(association)

        # TODO is this necessary on each iteration?
        try:
            db.session.add(recipe)
            db.session.commit()
        except (exc.IntegrityError, exc.DatabaseError):
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

        # grab these to be added back manually
        ingredients = new_recipe.pop('ingredients', None)

        # TODO schema complains about 'None is not list-like' if this isnt set
        # assume its due to ingredients being part of the model?
        new_recipe.update({'ingredients': []})

        RecipeSchema().update(recipe, new_recipe)

        if ingredients is not None:
            for ringredient in ingredients:
                ingredient = Ingredient.query.get(ringredient['ingredient_id'])

                if ingredient is None:
                    abort(422)

                association = RecipeIngredient(amount=ringredient['amount'], unit=ringredient['unit'])
                association.ingredient_id = ingredient.id
                association.ingredient = ingredient
                association.recipe_id = recipe.id
                association.recipe = recipe

                ingredient.recipes.append(association)
                recipe.ingredients.append(association)

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
    @blp.response(200, RIngredientSchema(many=True))
    def get(self, recipe_id):
        """Get ingredients associated with a recipe"""
        return Recipe.query.get_or_404(recipe_id).ingredients

    @blp.etag
    @blp.arguments(RIngredientSchema(many=True))
    @blp.response(204)
    def post(self, args, recipe_id):
        """Add association between a recipe and ingredient"""
        recipe = Recipe.query.get_or_404(recipe_id)

        for ringredient in args:
            ingredient = Ingredient.query.get(ringredient['ingredient_id'])

            if ingredient is None:
                abort(422)

            association = RecipeIngredient(amount=ringredient['amount'], unit=ringredient['unit'])
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
