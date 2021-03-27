from flask import jsonify, current_app
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

from ..common.httpstatuscodes import HttpStatusCodes
from ..database import db
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..models.tag import Tag

from datetime import datetime
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Name of the recipe')
parser.add_argument('steps', type=str, help='Steps to perform for recipe completion')
parser.add_argument('notes', type=str, help='Notes on the recipe')
parser.add_argument('rating', type=int, help='Rating for the recipe')
parser.add_argument('tags', type=str, help='Tags to search for, comma separated')
parser.add_argument('tag_ids', type=int, action='append', help='Ids of tags to associate with a recipe')

class Recipes(Resource):
    def get(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        return { recipe.id:recipe.to_dict() }, HttpStatusCodes.OK.value

    def patch(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()

        if args['name'] is not None:
            recipe.name = args['name']
        if args['steps'] is not None:
            recipe.steps = args['steps']
        if args['notes'] is not None:
            recipe.notes = args["notes"]
        if args['rating'] is not None:
            recipe.rating = args["rating"]
        # TODO Is this even necessary with the new RecipeTags endpoint?
        if args['tag_ids'] is not None:
            for tag_id in args['tag_ids']:
                tag = Tag.query.get(tag_id)
                if tag not in recipe.tags:
                    recipe.tags.append(tag)

                # silently pass if the tag is already associated with the recipe?

        if any(x is not None for x in args):
            recipe.last_modified = datetime.now()

        try:
            db.session.add(recipe)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.patch({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.patch({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.OK.value

    def delete(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        try:
            db.session.delete(recipe)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.delete({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.delete({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.NO_CONTENT.value

class RecipesTags(Resource):
    def get(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        return {x.to_dict() for x in recipe.tags}, HttpStatusCodes.OK.value

    def patch(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()

        # TODO Is this even necessary with the new RecipeTags endpoint?
        if args['tag_ids'] is not None:
            for tag_id in args['tag_ids']:
                tag = Tag.query.get(tag_id)
                if tag not in recipe.tags:
                    recipe.tags.append(tag)

                # silently pass if the tag is already associated with the recipe?
        else:
            return {'error':'No tag ids provided'}, HttpStatusCodes.BAD_REQUEST

        recipe.last_modified = datetime.now()

        try:
            db.session.add(recipe)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.patch({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.patch({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.OK.value

    def delete(self, recid):
        recipe = Recipe.query.get(recid)

        if recipe is None:
            return {"error":"No such recipe found"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()
        if args['tag_ids'] is not None:
            for tag_id in args['tag_ids']:
                tag = Tag.query.get(tag_id)

                # TODO alert the user?
                if tag is None or tag not in recipe.tags:
                    continue

                recipe.tags.remove(tag)
        # Not sure if deleting all tags will ever be desired?
        else:
            # TODO is there a built-in to do this in SQLAlchemy?
            for tag in recipe.tags:
                recipe.tags.remove(tag)

        try:
            db.session.add(recipe)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.delete({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Recipe.delete({recid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.NO_CONTENT.value

class RecipesList(Resource):
    def get(self):
        args = parser.parse_args()

        if args['name'] is not None:
            name = f"%{args['name']}%"
            recipes = Recipe.query.filter(Recipe.name.like(name)).all()
        elif args['tags'] is not None:
            tags = args['tags'].split(',')
            recipes = Recipe.query.filter(Recipe.tags.name in tags).all()
        else:
            recipes = Recipe.query.all()

        return {x.to_dict() for x in recipes}, HttpStatusCodes.OK.value

    def post(self):
        args = parser.parse_args()

        if args['name'] is None:
            return {"error":"A name is required for new recipes"}, HttpStatusCodes.BAD_REQUEST.value
        if args['steps'] is None:
            return {"error":"Steps are required for new recipes"}, HttpStatusCodes.BAD_REQUEST.value

        recipe = Recipe(name=args['name'], steps=args['steps'], notes=args['notes'], rating=args['rating'])

        try:
            db.session.add(recipe)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'RecipeList.post() -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'RecipeList.post() -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return [recipe.to_dict()], HttpStatusCodes.CREATED.value
