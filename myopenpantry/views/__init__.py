from . import ingredients
from . import items
from . import recipes

MODULES = (
    ingredients,
    items,
    recipes,
)

def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
