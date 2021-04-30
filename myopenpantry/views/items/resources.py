from flask.views import MethodView
from flask_smorest import abort
import sys
from sqlalchemy import exc

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Item, Ingredient

from .schemas import ItemSchema, ItemQueryArgsSchema
from ..ingredients.schemas import IngredientSchema

blp = Blueprint(
    'Items',
    __name__,
    url_prefix='/items',
    description="Operations on items"
)

# Trying to stay consistent with other error stuctures, eg: 
#"errors": {
#  "json": {
#    "ingredientId": [
#      "Must be greater than or equal to 0."
#    ]
#  }
#}, 
def handle_integrity_error_and_abort(e):
    # TODO surely there is a better way to figure out what the error type is?
    e = repr(e)
    errors = {'json':{}}
    if e.find('UNIQUE constraint failed: items.name'):
        errors['json']['name'] = ["Item with that name already exists"]
    if e.find('UNIQUE constraint failed: items.product_id'):
        errors['json']['productId'] = ["Item with that product ID already exists"]
    if e.find('FOREIGN KEY constraint failed'):
        errors['json']['ingredientId'] = ["No such ingredient with that id"]

    abort(422, errors=errors)

@blp.route('/')
class Items(MethodView):

    @blp.etag
    @blp.arguments(ItemQueryArgsSchema, location='query')
    @blp.response(200, ItemSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List all items or filter by args"""
        name = args.pop('name', None)

        ret = Item.query.filter_by(**args)

        if name is not None:
            ret = ret.filter(Item.name.like(f"%{name}%"))

        return ret.order_by(Item.id)

    @blp.etag
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, new_item):
        """Add a new item"""
        item = Item(**new_item)

        try:
            db.session.add(item)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except:
            db.session.rollback()
            # TODO check that Foreign Key failing is the only IntegrityError possible here? 
            abort(422, message="There was an error. Please try again.")

        return item

@blp.route('/<int:item_id>')
class ItemsById(MethodView):

    @blp.etag
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get item by ID"""
        return Item.query.get_or_404(item_id)

    @blp.etag
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def put(self, new_item, item_id):
        """Update an existing item"""
        item = Item.query.get_or_404(item_id)

        blp.check_etag(item, ItemSchema)

        ItemSchema().update(item, new_item)

        try:
            db.session.add(item)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except:
            db.session.rollback()
            # TODO check that Foreign Key failing is the only IntegrityError possible here? 
            abort(422, message="There was an error. Please try again.")

        return item

    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an item"""
        item = Item.query.get_or_404(item_id)

        blp.check_etag(item, ItemSchema)

        try:
            db.session.delete(item)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

@blp.route('/<int:item_id>/ingredient')
class ItemsIngredient(MethodView):

    @blp.etag
    @blp.response(200, IngredientSchema)
    def get(self, item_id):
        """Get the ingredient associated with the item"""
        return Item.query.get_or_404(item_id).ingredient

    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete the association between an item and ingredient"""
        item = Item.query.get_or_404(item_id)

        blp.check_etag(item, ItemSchema)

        item.ingredient_id = None

        try:
            db.session.add(item)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
