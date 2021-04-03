from flask.views import MethodView
from flask_smorest import abort

from sqlalchemy import or_

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

@blp.route('/')
class Items(MethodView):

    @blp.etag
    @blp.arguments(ItemQueryArgsSchema)
    @blp.response(200, ItemSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List all items"""
        names = args.pop('names', None)
        ingredient_ids = args.pop('ingredient_ids', None)
        product_ids = args.pop('product_ids', None)

        ret = Item.query.filter_by(**args)

        # TODO does marshmallow have a way to only allow one of these at a time?
        # product_id > ingredient_id > name for search order
        if product_ids is not None:
            ret = ret.filter(Item.product_id.in_(product_ids))
        elif ingredient_ids is not None:
            ret = ret.filter(Item.ingredient_id.in_(ingredient_ids))
        elif names is not None:
            # TODO SQLite does not have "ANY"
            # ret = ret.filter(Item.name.like(any_([f"%{name}%" for name in names])))
            ret = ret.filter(or_(Item.name.like(f"%{name}%") for name in names))

        return ret

    @blp.etag
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, new_item):
        """Add a new item"""
        item = Item(**new_item)
        try:
            db.session.add(item)
            db.session.commit()
        except:
            db.session.rollback()
            # TODO be more descriptive and log
            abort(422)
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
        except:
            db.session.rollback()
            # TODO be more descriptive and log
            abort(422)
        return item

    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an item"""
        item = Item.query.get_or_404(item_id)
        blp.check_etag(item, ItemSchema)
        db.session.delete(item)
        db.session.commit()

@blp.route('/<int:item_id>/ingredient')
class ItemsIngredient(MethodView):

    @blp.etag
    @blp.response(200, IngredientSchema)
    def get(self, item_id):
        """Get the ingredient associated with the item"""
        return Item.query.get_or_404(item_id).ingredient
