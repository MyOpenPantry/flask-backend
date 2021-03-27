import pytest
from datetime import datetime
from pantryapi import db

from ..models.ingredient import Ingredient
from ..models.inventoryitem import InventoryItem
from ..models.recipe import Recipe
from ..models.tag import Tag
from ..models.associations import inventory_ingredients, recipe_tags, Association

def test_inventoryitem(client):
    """
        Test adding and retrieving an InventoryItem
    """
    start_time = datetime.now()
    item = InventoryItem(name="Eggs", amount=12, product_id=12345)

    assert item.name == 'Eggs'
    assert item.amount == 12
    assert item.product_id == 12345

    db.session.add(item)
    db.session.commit()

    retrieved_item = InventoryItem.query.get(item.id)

    assert item.updated >= start_time
    assert item == retrieved_item

def test_recipe(client):
    """
        Test adding, retrieving, and modifying a Recipe
    """
    start_time = datetime.now()
    steps = """
        step 1: some action
        step 2: another action
        step 3: have some fun
        step 4: eat
    """

    recipe = Recipe(name="Eggs Benedict", steps=steps, notes="Very good!", rating=5)

    assert recipe.name == "Eggs Benedict"
    assert recipe.steps == steps
    assert recipe.notes == "Very good!"
    assert recipe.rating == 5

    db.session.add(recipe)
    db.session.commit()

    retrieved_recipe = Recipe.query.get(recipe.id)

    assert retrieved_recipe.created_at >= start_time
    assert retrieved_recipe.last_modified >= start_time

    recipe.rating = 6

    db.session.add(recipe)
    db.session.commit()

    retrieved_recipe = Recipe.query.get(recipe.id)

    assert retrieved_recipe.last_modified > retrieved_recipe.created_at

def test_tag(client):
    """
        Test adding and retrieving a Tag
    """
    start_time = datetime.now()
    tag = Tag(name="egg")

    assert tag.name == 'egg'

    db.session.add(tag)
    db.session.commit()

    retrieved_tag = Tag.query.get(tag.id)

    assert tag == retrieved_tag

def test_ingredient(client):
    """
        Test adding and retrieving an Ingredient
    """
    start_time = datetime.now()
    ingredient = Ingredient(name="Eggs")

    assert ingredient.name == 'Eggs'

    db.session.add(ingredient)
    db.session.commit()

    retrieved_ingredient = Ingredient.query.get(ingredient.id)

    assert ingredient == retrieved_ingredient

def test_ingredient_recipe_association(client):
    """
        Test adding and removing an association between a Recipe and an Ingredient
    """
    start_time = datetime.now()

    eggs = Ingredient(name="Eggs")
    eggs_association = Association(amount=12, unit="eggs")
    eggs_association.ingredient = eggs

    hollandaise = Ingredient(name="Hollandaise Sauce")
    hollandaise_association = Association(amount=0.5, unit="cup")
    hollandaise_association.ingredient = hollandaise

    bacon = Ingredient(name="Canadian Bacon")
    bacon_association = Association(amount=2, unit="slices")
    bacon_association.ingredient = bacon

    steps = """
        step 1: some action
        step 2: another action
        step 3: have some fun
        step 4: eat
    """
    recipe = Recipe(name="Eggs Benedict", steps=steps, notes="Very good!", rating=5)
    recipe.ingredients.append(eggs_association)
    recipe.ingredients.append(hollandaise_association)
    recipe.ingredients.append(bacon_association)

    db.session.add(recipe)
    db.session.commit()

    # verify that the association was created
    assert len(recipe.ingredients) == 3
    assert eggs_association in recipe.ingredients
    assert hollandaise_association in recipe.ingredients
    assert bacon_association in recipe.ingredients

    # remove bacon from the recipe
    db.session.delete(bacon_association)

    db.session.commit()

    # make sure just the association was deleted, bacon should still exist as an ingredient
    assert len(recipe.ingredients) == 2
    assert bacon_association not in recipe.ingredients
    assert Ingredient.query.get(bacon.id) is not None
    assert len(Ingredient.query.all()) == 3

def test_recipe_tag_association(client):
    """
        Test adding and removing a Tag to a Recipe
    """

    tag_greek = Tag(name="greek")
    tag_chicken = Tag(name="chicken")

    recipe_greek = Recipe(name="Greek chicken", steps="", rating=3, notes="Yummy")
    recipe_greek.tags.append(tag_greek)
    recipe_greek.tags.append(tag_chicken)

    db.session.add_all([
        recipe_greek,
        tag_chicken,
        tag_greek
    ])
    db.session.commit()

    assert len(recipe_greek.tags) == 2
    assert recipe_greek in tag_greek.recipes
    assert recipe_greek in tag_chicken.recipes

    tag_garlic = Tag(name="garlic")

    recipe_chicken = Recipe(name="Garlic chicken", steps="brush chicken in garlic and cook in oven", rating=9, notes="The best")
    recipe_chicken.tags.append(tag_chicken)
    recipe_chicken.tags.append(tag_garlic)

    db.session.add_all([
        recipe_chicken,
        tag_garlic
    ])
    db.session.commit()

    assert recipe_chicken not in tag_greek.recipes
    assert recipe_greek not in tag_garlic.recipes
    assert len(tag_chicken.recipes) == 2

    recipe_greek.tags.remove(tag_greek)

    db.session.add_all([
        recipe_greek,
        tag_greek
    ])
    db.session.commit()

    assert recipe_greek not in tag_greek.recipes
    assert tag_greek not in recipe_greek.tags
    assert len(Tag.query.all()) == 3

def test_inventoryitem_ingredient_association(client):
    """
        Test adding an Ingredient to an InventoryItem
    """

    start_time = datetime.now()
    eggs = Ingredient(name="Eggs")
    kroger_eggs = InventoryItem(name="Kroger Eggs", amount=12, product_id=12345)
    costco_eggs = InventoryItem(name="Costco Eggs", amount=13, product_id=54321)

    db.session.add_all([
        eggs,
        kroger_eggs,
        costco_eggs
    ])
    db.session.commit()

    assert len(eggs.inventory_items) == 0
    assert kroger_eggs.ingredient is None
    assert costco_eggs.ingredient is None

    kroger_eggs.ingredient = eggs
    costco_eggs.ingredient = eggs

    db.session.add_all([
        eggs,
        kroger_eggs,
        costco_eggs,
    ])
    db.session.commit()

    costco_eggs.ingredient = None

    db.session.add(costco_eggs)
    db.session.commit()

    assert costco_eggs.ingredient is None
    assert kroger_eggs.ingredient == eggs
