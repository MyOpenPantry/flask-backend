from flask import jsonify, current_app
from flask_restful import Resource, reqparse, fields, marshal
from flask_sqlalchemy import SQLAlchemy

from ..common.httpstatuscodes import HttpStatusCodes
from ..database import db
from ..models.inventoryitem import InventoryItem
from ..models.ingredient import Ingredient

from datetime import datetime
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Name of the inventory item')
parser.add_argument('product_id', type=int, help='Product id of the inventory item')
parser.add_argument('amount', type=int, help='Number of units of the inventory item')
parser.add_argument('ingredient_id', type=int, help='Id of the ingredient type the inventory item belongs to')

inventory_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'product_id': fields.Integer,
    'amount': fields.Integer,
    'updated': fields.DateTime,
    'ingredient_id': fields.Integer(default=None),
    #'links': fields.Nested({
    #    'ingredient': fields.Url('ingredients/{ingredient_id}', absolute=True),
    #}),
}

def check_ingredient_id(ingredient_id):
    try:
        ingredient_id = int(ingredient_id)
    except TypeError:
        raise TypeError(f'Ingredient id must be an integer')

    ingredient = Ingredient.query.get(ingredient_id)

    if ingredient is None:
        raise LookupError(f'No ingredient exists with id {ingredient_id}')
    else:
        return ingredient_id

class Inventory(Resource):

    #@marshal_with(inventory_fields)
    def get(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        return item, HttpStatusCodes.OK.value

    def patch(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()

        if args['name'] is not None:
            item.name = args['name']
        if args['product_id'] is not None:
            item.product_id = args['product_id']
        if args['amount'] is not None:
            item.amount = args['amount']
        if args['ingredient_id'] is not None:
            ingredient = Ingredient.query.get(args['ingredient_id'])
            
            if ingredient is None:
                return {"error":"No ingredient exists with that id. Transaction not committed"}, HttpStatusCodes.NOT_FOUND.value

            item.ingredient_id = ingredient.id
            item.ingredient = ingredient

        if any(x is not None for x in args):
            item.updated = datetime.now()

        try:
            db.session.add(item)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Inventory.patch({invid}) -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Inventory.patch({invid}) -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.OK.value

    def delete(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        try:
            db.session.delete(item)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'Inventory.delete({invid}) -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Inventory.delete({invid}) -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.NO_CONTENT.value

class InventoryList(Resource):

    def post_parser(self):
        parser = reqparse.RequestParser()
        # Help is returned when the argument doesn't match the function provided in type, so use it as an error message
        parser.add_argument('name', type=str, required=True, help='No name was provided for the item')
        parser.add_argument('amount', type=int, required=True, help='amount must be an integer')
        parser.add_argument('product_id', type=int, help='product id must be an integer')
        parser.add_argument('ingredient_id', type=int, help='ingredient_id must be an integer')
        return parser

    #@marshal_with(inventory_fields)
    def get(self):
        args = parser.parse_args()

        if args['name'] is not None:
            name = f"%{args['name']}%"
            inventory_items = InventoryItem.query.filter(InventoryItem.name.like(name)).all()
        else:
            inventory_items = InventoryItem.query.all()

        return [x for x in inventory_items], HttpStatusCodes.OK.value

    #@marshal_with(inventory_fields)
    def post(self):
        args = self.post_parser().parse_args()

        item = InventoryItem(name=args['name'], product_id=args['product_id'], amount=args['amount'])

        if args['ingredient_id'] is not None:
            ingredient = Ingredient.query.get(args['ingredient_id'])
            #item.ingredient_id = ingredient.id
            item.ingredient = ingredient

        try:
            db.session.add(item)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            current_app.logger.error(f'[InventoryList.post() -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'[Inventory.post()] -> \"{e}\"')
            return {"message":{"error":"Error committing transaction"}}, HttpStatusCodes.CONFLICT.value

        return {'item': marshal(item, inventory_fields)}
