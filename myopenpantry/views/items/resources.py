from flask.views import MethodView

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Item, Ingredient

from .schemas import ItemSchema, ItemQueryArgsSchema

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
        """List items"""
        name = args.pop('name', None)
        ingredient_id = args.pop('ingredient_id', None)
        product_id = args.pop('product_id', None)

        ret = Item.query.filter_by(**args)
        if product_id is not None:
            ret = ret.filter(Item.product_id == product_id)
            #ret = Item.query.filter(Item.product_id == product_id)
        if ingredient_id is not None:
            ret = ret.filter(Item.ingredient_id == ingredient_id)
            #ret = Item.query.filter(Item.ingredient_id == ingredient_id)
        if name is not None:
            name = f"%{name}%"
            ret = ret.filter(Item.name.like(name))
            #ret = Item.query.filter(Item.name.like(name))
        #else:

        return ret

    @blp.etag
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, new_item):
        """Add a new item"""
        item = Item(**new_item)
        db.session.add(item)
        db.session.commit()
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
        db.session.add(item)
        db.session.commit()
        return item

    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an item"""
        item = Item.query.get_or_404(item_id)
        blp.check_etag(item, ItemSchema)
        db.session.delete(item)
        db.session.commit()
