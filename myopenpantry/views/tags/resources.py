from flask.views import MethodView
from flask_smorest import abort

from sqlalchemy import exc

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Tag
from ..recipes.schemas import RecipeSchema, TagSchema, TagQueryArgsSchema

blp = Blueprint(
    'Tags',
    __name__,
    url_prefix='/tags',
    description="Operations on tags"
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
    if e.find('UNIQUE constraint failed: tags.name') != -1:
        errors['json']['name'] = ["Tag with that name already exists"]

    abort(422, errors=errors)


@blp.route('/')
class Tags(MethodView):

    @blp.etag
    @blp.arguments(TagQueryArgsSchema, location='query')
    @blp.response(200, TagSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List tags"""
        name = args.pop('name', None)

        ret = Tag.query.filter_by(**args)

        if name is not None:
            ret = ret.filter(Tag.name.like(f"%{name}%"))

        return ret.order_by(Tag.id)

    @blp.etag
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, new_tag):
        """Add a new tag"""
        tag = Tag(**new_tag)

        try:
            db.session.add(tag)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")

        return tag


@blp.route('/<int:tag_id>')
class TagsbyID(MethodView):

    @blp.etag
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """Get tag by ID"""
        return Tag.query.get_or_404(tag_id)

    @blp.etag
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, new_tag, tag_id):
        """Update an existing tag"""
        tag = Tag.query.get_or_404(tag_id)

        blp.check_etag(tag, TagSchema)

        TagSchema().update(tag, new_tag)

        try:
            db.session.add(tag)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            handle_integrity_error_and_abort(e)
        except exc.DatabaseError:
            db.session.rollback()
            abort(422, message="There was an error. Please try again.")

        return tag

    @blp.etag
    @blp.response(204)
    def delete(self, tag_id):
        """Delete a tag"""
        tag = Tag.query.get_or_404(tag_id)

        blp.check_etag(tag, TagSchema)

        db.session.delete(tag)
        db.session.commit()


@blp.route('/<int:tag_id>/recipes')
class TagRecipes(MethodView):

    @blp.etag
    @blp.response(200, RecipeSchema(many=True))
    def get(self, tag_id):
        """Get recipes associated with a tag"""
        return Tag.query.get_or_404(tag_id).recipes
