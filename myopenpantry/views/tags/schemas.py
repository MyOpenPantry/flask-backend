import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from myopenpantry.extensions.api import Schema, AutoSchema
from myopenpantry.models.tags import Tag

class TagSchema(AutoSchema):
    id = field_for(Tag, "id", dump_only=True)

    class Meta(AutoSchema.Meta):
        table = Tag.__table__

class TagQueryArgsSchema(Schema):
    names = ma.fields.List(ma.fields.Str(validate=ma.validate.Length(min=1)))
    recipe_ids = ma.fields.List(ma.fields.Int(strict=True, validate=ma.validate.Range(min=1)))
