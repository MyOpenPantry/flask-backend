from flask import jsonify
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

from ..models.inventoryitem import InventoryItem
from ..database import db
from datetime import datetime
import sys

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Name of the inventory item')
parser.add_argument('upc', type=int, help='UPC of the inventory item')
parser.add_argument('amount', type=int, help='Number of units of the inventory item')

class Inventory(Resource):
    def get(self, invid):
        item = InventoryItem.query.get(invid)
        if item is None:
            return {"error":"No such item in the pantry"}
        return { f"{item.id}":f"{item.name}" }, 201

    def put(self, invid):
        item = InventoryItem.query.get(invid)
        if item is None:
            return {"error":"No such item in the pantry"}

        args = parser.parse_args()

        if args['name'] is not None:
            item.name = args['name']
        if args['upc'] is not None:
            item.upc = args['upc']
        if args['amount'] is not None:
            item.amount = args["amount"]

        item.updated = datetime.now()

        try:
            db.session.add(item)
            db.session.commit()
        except:
            db.session.rollback()
            return {"error":"Error commiting transaction"}
        return '', 201

class InventoryList(Resource):
    def get(self):
        args = parser.parse_args()

        if args["name"] is not None:
            name = f"%{args['name']}%"
            inventory_items = InventoryItem.query.filter(InventoryItem.name.like(name)).all()
        else:
            inventory_items = InventoryItem.query.all()
        print(inventory_items)
        return jsonify([x.to_dict() for x in inventory_items])

    def post(self):
        args = parser.parse_args()
        # TODO do actual valdiation (after initial protoype is done). Also, UPC-A is 12 digits and EAN-13 is ... 13
        if args['upc'] > 9999999999999:
            return {'error': 'upc cannot exceed 13 digits.'}

        new_item = InventoryItem(name=args['name'], upc=args['upc'], amount=args['amount'])
        try:
            db.session.add(new_item)
            db.session.commit()
        except:
            db.session.rollback()
            return {"error":"Error commiting transaction"}
        return '', 201
