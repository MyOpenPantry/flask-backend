from flask import jsonify
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

from ..common.httpstatuscodes import HttpStatusCodes
from ..database import db
from ..models.inventoryitem import InventoryItem

from datetime import datetime
import sys

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Name of the inventory item')
parser.add_argument('productId', type=int, help='Product id of the inventory item')
parser.add_argument('amount', type=int, help='Number of units of the inventory item')

class Inventory(Resource):
    def get(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        return { item.id:item.to_dict() }, HttpStatusCodes.OK.value

    def patch(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        args = parser.parse_args()

        if args['name'] is not None:
            item.name = args['name']
        if args['productId'] is not None:
            item.productId = args['productId']
        if args['amount'] is not None:
            item.amount = args["amount"]

        item.updated = datetime.now()

        try:
            db.session.add(item)
            db.session.commit()
        except db.exc.DBAPIError as e:
            db.session.rollback()
            app.logger.error(f'[Inventory.put({invid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except db.exc.SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'[Inventory.put({invid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.OK.value

    def delete(self, invid):
        item = InventoryItem.query.get(invid)

        if item is None:
            return {"error":"No such item in the pantry"}, HttpStatusCodes.NOT_FOUND.value

        try:
            db.session.delete(item)
            db.session.commit()
        except db.exc.DBAPIError as e:
            db.session.rollback()
            app.logger.error(f'[Inventory.delete({invid}) -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except db.exc.SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'[Inventory.delete({invid})] -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return '', HttpStatusCodes.NO_CONTENT.value

class InventoryList(Resource):
    def get(self):
        args = parser.parse_args()

        if args["name"] is not None:
            name = f"%{args['name']}%"
            inventory_items = InventoryItem.query.filter(InventoryItem.name.like(name)).all()
        else:
            inventory_items = InventoryItem.query.all()

        return {x.id:x.to_dict() for x in inventory_items}, HttpStatusCodes.OK.value

    def post(self):
        args = parser.parse_args()

        if args['name'] is None:
            return {"error":"A name is required for new inventory items"}, HttpStatusCodes.BAD_REQUEST.value

        if args['amount'] is None:
            args['amount'] = 0

        new_item = InventoryItem(name=args['name'], product_id=args['productId'], amount=args['amount'])

        try:
            db.session.add(new_item)
            db.session.commit()
        except db.exc.DBAPIError as e:
            db.session.rollback()
            app.logger.error(f'[InventoryList.post() -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.INTERNAL_SERVER_ERROR.value
        except db.exc.SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'[Inventory.post()] -> \"{e}\"')
            return {"error":"Error committing transaction"}, HttpStatusCodes.CONFLICT.value

        return {new_item.id:new_item.to_dict()}, HttpStatusCodes.CREATED.value
