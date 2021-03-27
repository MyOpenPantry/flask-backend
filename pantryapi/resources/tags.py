from flask import jsonify, current_app
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

from ..common.httpstatuscodes import HttpStatusCodes
from ..database import db
from ..models.tag import Tag
from ..models.recipe import Recipe

from datetime import datetime
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Name of the tag')
parser.add_argument('recipe_id', type=int, help='Id of the recipe to link with a tag')

class Tags(Resource):
    def get(self, tagid):
        tag = Tag.query.get(tagid)

        if tag is None:
            return {"error":"No such tag"}, HttpStatusCodes.NOT_FOUND.value

        return {tag.to_dict()}, HttpStatusCodes.OK.value

    def patch(self, tagid):
        tag = Tag.query.get(tagid)

        if tag is None:
            return {"error":"No such tag"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()

        if args['name'] is not None:
            tag.name = args['name']
        if args['recipe_id'] is not None:
            recipe = Recipe.query.get(args['recipe_id'])
            
            if recipe is None:
                return {"error":"No recipe exists with that id. Transaction not committed"}, HttpStatusCodes.NOT_FOUND.value

            tag.recipes.append(recipe)

        try:
            db.session.add(tag)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Tag.patch({tagid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Tag.patch({tagid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.OK.value

    def delete(self, tagid):
        tag = Tag.query.get(tagid)

        if tag is None:
            return {"error":"No such tag"}, HttpStatusCodes.NOT_FOUND.value

        try:
            db.session.delete(tag)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Tag.delete({invid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Tag.delete({invid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.NO_CONTENT.value

class TagsList(Resource):
    def get(self):
        args = parser.parse_args()

        if args['name'] is not None:
            name = f"%{args['name']}%"
            tags = Tag.query.filter(Tag.name.like(name)).all()
        else:
            tags = Tag.query.all()

        return {x.to_dict() for x in tags}, HttpStatusCodes.OK.value

    def post(self):
        args = parser.parse_args()

        if args['name'] is None:
            return {"error":"A name is required for new tags"}, HttpStatusCodes.BAD_REQUEST.value

        tag = Tag(name=args['name'])

        if args['recipe_id'] is not None:
            recipe = Recipe.query.get(args['recipeId'])

            if recipe is None:
                return {"error":"No recipe exists with that id. Transaction not committed"}, HttpStatusCodes.NOT_FOUND.value

            tag.recipes.append(recipe)

        try:
            db.session.add(tag)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'TagList.post() -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'TagList.post() -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return {tag.to_dict()}, HttpStatusCodes.CREATED.value
