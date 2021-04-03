from flask.views import MethodView

from myopenpantry.extensions.api import Blueprint, SQLCursorPage
from myopenpantry.extensions.database import db
from myopenpantry.models import Tag

from .schemas import TagSchema, TagQueryArgsSchema
from ..recipes.schemas import RecipeSchema

blp = Blueprint(
    'Tags',
    __name__,
    url_prefix='/tags',
    description="Operations on tags"
)

@blp.route('/')
class Tags(MethodView):

    @blp.etag
    @blp.arguments(TagQueryArgsSchema)
    @blp.response(200, TagSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List tags"""
        recipe_ids = args.pop('recipe_id', None)

        ret = Tag.query.filter_by(**args)

        if recipe_ids is not None:
            ret = ret.filter(Tag.recipes.id in recipe_ids)

        return ret

    @blp.etag
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, new_tag):
        """Add a new tag"""
        tag = Tag(**new_tag)

        try:
            db.session.add(tag)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

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

        RecipeSchema().update(tag, new_tag)

        try:
            db.session.add(tag)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)

        return tag

    @blp.etag
    @blp.response(204)
    def delete(self, recipe_id):
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
        return Tags.query.get_or_404(tag_id).recipes

@blp.route('/<int:tag_id>/recipes/<int:recipe_id>')
class TagRecipesDelete(MethodView):

    @blp.etag
    @blp.response(204)
    def delete(self, tag_id, recipe_id):
        """Delete association between a tag and recipe"""
        tag = Tag.query.get_or_404(tag_id)
        recipe = tags.recipe.get_or_404(recipe_id)

        blp.check_etag(tag, TagSchema)

        tag.recipes.remove(recipe)

        try:
            db.session.add(tag)
            db.session.commit()
        except:
            db.session.rollback()
            abort(422)
