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
    test_item = InventoryItem(name="Eggs", amount=12, product_id=12345)

    assert test_item.name == 'Eggs'
    assert test_item.amount == 12
    assert test_item.product_id == 12345

    db.session.add(test_item)
    db.session.commit()

    retrieved_item = InventoryItem.query.get(test_item.id)

    assert test_item.updated >= start_time
    assert test_item == retrieved_item

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

    test_recipe = Recipe(name="Eggs Benedict", steps=steps, notes="Very good!", rating=5)

    assert test_recipe.name == "Eggs Benedict"
    assert test_recipe.steps == steps
    assert test_recipe.notes == "Very good!"
    assert test_recipe.rating == 5

    db.session.add(test_recipe)
    db.session.commit()

    retrieved_recipe = Recipe.query.get(test_recipe.id)

    assert retrieved_recipe.created_at >= start_time
    assert retrieved_recipe.last_modified >= start_time

    test_recipe.rating = 6

    db.session.add(test_recipe)
    db.session.commit()

    retrieved_recipe = Recipe.query.get(test_recipe.id)

    assert retrieved_recipe.last_modified > retrieved_recipe.created_at

def test_tag(client):
    """
        Test adding and retrieving a Tag
    """
    start_time = datetime.now()
    test_tag = Tag(name="egg")

    assert test_tag.name == 'egg'

    db.session.add(test_tag)
    db.session.commit()

    retrieved_tag = Tag.query.get(test_tag.id)

    assert test_tag == retrieved_tag

def test_ingredient(client):
    """
        Test adding and retrieving an Ingredient
    """
    start_time = datetime.now()
    test_ingredient = Ingredient(name="Eggs")

    assert test_ingredient.name == 'Eggs'

    db.session.add(test_ingredient)
    db.session.commit()

    retrieved_ingredient = Ingredient.query.get(test_ingredient.id)

    assert test_ingredient == retrieved_ingredient

def test_ingredient_recipe_association(client):
    """
        Test adding and removing an association between a Recipe and an Ingredient
    """
    start_time = datetime.now()

    test_eggs = Ingredient(name="Eggs")
    test_eggs_association = Association(amount=12, unit="eggs")
    test_eggs_association.ingredient = test_eggs

    test_hollandaise = Ingredient(name="Hollandaise Sauce")
    test_hollandaise_association = Association(amount=0.5, unit="cup")
    test_hollandaise_association.ingredient = test_hollandaise

    test_bacon = Ingredient(name="Canadian Bacon")
    test_bacon_association = Association(amount=2, unit="slices")
    test_bacon_association.ingredient = test_bacon

    steps = """
        step 1: some action
        step 2: another action
        step 3: have some fun
        step 4: eat
    """
    test_recipe = Recipe(name="Eggs Benedict", steps=steps, notes="Very good!", rating=5)
    test_recipe.ingredients.append(test_eggs_association)
    test_recipe.ingredients.append(test_hollandaise_association)
    test_recipe.ingredients.append(test_bacon_association)

    db.session.add(test_recipe)
    db.session.commit()

    # verify that the association was created
    assert len(test_recipe.ingredients) == 3
    assert test_eggs_association in test_recipe.ingredients
    assert test_hollandaise_association in test_recipe.ingredients
    assert test_bacon_association in test_recipe.ingredients

    # remove bacon from the recipe
    db.session.delete(test_bacon_association)

    db.session.commit()

    # make sure just the association was deleted, bacon should still exist as an ingredient
    assert len(test_recipe.ingredients) == 2
    assert test_bacon_association not in test_recipe.ingredients
    assert Ingredient.query.get(test_bacon.id) is not None
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

    pass