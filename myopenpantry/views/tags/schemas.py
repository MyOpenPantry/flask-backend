import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.recipes import Tag

class TagSchema(AutoSchema):
    id = field_for(Tag, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Tag.__table__

class TagQueryArgsSchema(Schema):
    name = ma.fields.Str()
    recipe_id = ma.fields.Int()
