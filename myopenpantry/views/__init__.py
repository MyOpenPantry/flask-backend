from . import ingredients
from . import items
from . import recipes
from . import tags

MODULES = (
    ingredients,
    items,
    recipes,
    tags,
)

def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
