import pytest, json
from datetime import datetime
import dateutil.parser

class TestItemIngredients:
    def test_link_item_ingredient(self, app):
        client = app.test_client()

        # create an item with no ingredient id set
        new_item1 = {
            'name':'Kroger Chicken Thighs',
            'amount':6,
            'product_id':1111111111111,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item1,
        )

        assert response.status_code == 201

        item1_id = response.json['id']
        item1_etag = response.headers['ETag']

        # create an ingredient
        new_ingredient = {
            'name':'chicken thighs',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = new_ingredient,
        )

        assert response.status_code == 201

        ingredient_id = response.json['id']

        # create another new item, this time with the newly created ingredient id
        new_item2 = {
            'name':'Costco Chicken Thighs',
            'amount':2,
            'product_id':2222222222222,
        }

        response = client.post(f'/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item2,
        )

        assert response.status_code == 201

        # update the first item to use the ingredient
        new_item1['ingredient_id'] = ingredient_id
        response = client.put(f'/items/{item1_id}', 
            headers = {"If-Match": item1_etag},
            json = new_item1,
        )

        assert response.status_code == 200
        assert response.json['ingredient_id'] == ingredient_id

    def test_unlinking(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'vegetable',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = new_ingredient,
        )

        assert response.status_code == 201

        ingredient_id = response.json['id']

        new_item = {
            'name':'Asparagus',
            'amount':2,
            'product_id':54,
            'ingredient_id': ingredient_id
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        del new_item['ingredient_id']
        response = client.put(f'/items/{id}',
            headers = {'If-Match': etag},
            json = new_item
        )

        assert response.status_code == 200
        assert response.json.get('ingredient_id', None) is None

        # check that the ingredient wasn't deleted
        response = client.get(f'/ingredients/{ingredient_id}')

        assert response.status_code == 200

    # sqlite doesn't enforce foreign key constraints by default so test that it is enabled (extensions/database/__init__.py)
    def test_invalid_ingredient(self, app):
        client = app.test_client()

        new_item = {
            'name':'Rutabaga',
            'amount':9999,
            'product_id':4412,
            'ingredient_id': 1
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item,
        )

        assert response.status_code == 422

    def test_get_item_ingredient(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'grape',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = new_ingredient,
        )

        assert response.status_code == 201

        ingredient = response.json

        new_item = {
            'name':'Champagne Grapes',
            'amount':567,
            'ingredient_id': ingredient['id']
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item,
        )

        assert response.status_code == 201

        item = response.json

        response = client.get(f'/items/{item["id"]}/ingredient')

        assert response.status_code == 200
        assert response.json == ingredient
