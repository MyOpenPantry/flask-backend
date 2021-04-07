import pytest, json
from datetime import datetime
import dateutil.parser

class TestItemIngredients:
    def test_link_get(self, app):
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

        # create another item, this time with the newly created ingredient id
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

        response = client.get(f'/items/{item1_id}/ingredient')

        assert response.status_code == 200
        assert response.json['id'] == ingredient_id

        response = client.get(f'/ingredients/{ingredient_id}/items')

        assert response.status_code == 200
        assert response.json[0]['id'] == item1_id

        ingredient_etag = response.headers['ETag']

        # create another item, this time with the newly created ingredient id
        new_item3 = {
            'name':'Aldi Chicken Thighs',
            'amount':46,
        }

        response = client.post(f'/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item3,
        )

        assert response.status_code == 201
        item3_id = response.json['id']

        # add association from ingredients/id/items
        response = client.post(f'ingredients/{ingredient_id}/items',
            headers = {'Content-Type':'application/json'},
            json = {'item_id':item3_id}
        )

        assert response.status_code == 204

        # verfiy it worked
        response = client.get(f'/items/{item3_id}/ingredient')

        assert response.status_code == 200
        assert response.json['id'] == ingredient_id

    def test_unlink(self, app):
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

        # remove the ingredient association via put on items/id
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

        # obtain the new etag for the item
        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # Add the ingredient back so deleting from items/id/ingredient can be tested
        new_item['ingredient_id'] = ingredient_id
        response = client.put(f'/items/{id}', 
            headers = {"If-Match": etag},
            json = new_item
        )

        assert response.status_code == 200
        assert response.json['ingredient_id'] == ingredient_id

        # obtain the new etag for the item
        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # delete the association from items/id/ingredient this time
        response = client.delete(f'/items/{id}/ingredient',
            headers = {'If-Match': etag},
        )

        assert response.status_code == 204

        # check that the ingredient wasn't deleted
        response = client.get(f'/ingredients/{ingredient_id}')

        assert response.status_code == 200



        # obtain the new etag for the item
        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # Add the ingredient back so deleting from items/id/ingredient can be tested
        new_item['ingredient_id'] = ingredient_id
        response = client.put(f'/items/{id}', 
            headers = {"If-Match": etag},
            json = new_item
        )

        assert response.status_code == 200
        assert response.json['ingredient_id'] == ingredient_id

        # obtain the new etag for the ingredient
        response = client.get(f'/ingredients/{ingredient_id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # delete the association from items/id/ingredient this time
        response = client.delete(f'/ingredients/{ingredient_id}/items/{id}',
            headers = {'If-Match': etag},
        )

        assert response.status_code == 204

        # check that the ingredient wasn't deleted
        response = client.get(f'/items/{id}')

        assert response.status_code == 200

        # try again to make sure abort is used when an incorrect item_id is used
        response = client.delete(f'/ingredients/{ingredient_id}/items/{id}',
            headers = {'If-Match': etag},
        )

        assert response.status_code == 422


    # sqlite doesn't enforce foreign key constraints by default so test that it is enabled (extensions/database/__init__.py)
    def test_link_invalid(self, app):
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

        # remove the invalid ingredient_id so there is a real item to work with
        del new_item['ingredient_id']
        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = new_item,
        )

        assert response.status_code == 201

        item_id = response.json['id']

        # create an ingredient
        new_ingredient = {
            'name':'rutabaga',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = new_ingredient,
        )

        assert response.status_code == 201

        ingredient_id = response.json['id']

        # invalid item id
        response = client.post(f'ingredients/{ingredient_id}/items',
            headers = {'Content-Type':'application/json'},
            json = {'item_id':item_id + 1}
        )

        assert response.status_code == 422
