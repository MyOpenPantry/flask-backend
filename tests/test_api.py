import pytest, json
from datetime import datetime
import dateutil.parser

class TestItems:
    def test_get_item(self, app):
        client = app.test_client()

        response = client.get('/items/')
        assert response.status_code == 200
        assert response.json == []

    def test_post_item(self, app):
        client = app.test_client()

        new_item = {
            'name':'Kroger Eggs',
            'amount':12,
            'product_id':123456,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        for k,v in new_item.items():
            assert response.json[k] == v

    def test_put_item(self, app):
        client = app.test_client()

        new_item = {
            'name':'Peanut Butter',
            'amount':1,
            'product_id':1000239983223,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 201

        id = response.json['id']
        updated = response.json['updated']
        etag = response.headers['ETag']

        update_item = {
            'name':'Peanut Butter',
            'amount':2,
            'product_id':1000239983223,
        }
        response = client.put(f'/items/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 200

        response = client.get(f'/items/{id}') 

        assert response.status_code == 200
        assert dateutil.parser.parse(response.json['updated']) > dateutil.parser.parse(updated)

    def test_invalid_put_item(sel, app):
        client = app.test_client()

        new_item = {
            'name':'Grape Jelly',
            'amount':44,
            'product_id':1033239983223,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 201

        id = response.json['id']
        updated = response.json['updated']
        etag = response.headers['ETag']

        # updated is read only
        update_item = {
            'name':'Grape Jelly',
            'amount':44,
            'product_id':1033239983223,
            'updated':'2021-03-30T14:55:30.500000'
        }
        response = client.put(f'/items/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 422

        # no name
        update_item = {
            'amount':44,
        }
        response = client.put(f'/items/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 422

        # no amount
        update_item = {
            'name':'Grape Jelly',
        }
        response = client.put(f'/items/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 422

    def test_query_item(self, app):
        client = app.test_client()

        # Add ingredients here so we can search by them
        new_ingredients = [
            {
                'name':'eggs'
            },
            {
                'name':'chicken breast'
            },
        ]

        # collect ingredient ids for searching later
        ingredient_ids = {}

        for ingredient in new_ingredients:
            response = client.post('/ingredients/', 
                headers = {"Content-Type": "application/json"},
                data = json.dumps(ingredient),
            )
            assert response.status_code == 201

            ingredient_ids[ingredient['name']] = response.json['id']

        new_items = [
            {
                'name':'Kroger Eggs',
                'amount':12,
                'product_id':123456,
                'ingredient_id':ingredient_ids['eggs']
            },
            {
                'name':'Kroger Chicken Breast',
                'amount':11,
                'product_id':123,
                'ingredient_id':ingredient_ids['chicken breast']
            },
            {
                'name':'Costco Chicken Breast',
                'amount':3,
                'product_id':2323,
                'ingredient_id':ingredient_ids['chicken breast']
            },
            {
                'name':'Aldi Beef Chuck',
                'amount':2,
                'product_id':4444,
            },
            {
                'name':'Bananas',
                'amount':1,
            },
            {
                'name':'Apples',
                'amount':5,
            },
        ]

        for item in new_items:
            response = client.post('/items/', 
                headers = {"Content-Type": "application/json"},
                data = json.dumps(item),
            )
            assert response.status_code == 201

        response = client.get('/items/')

        assert response.status_code == 200
        assert len(response.json) == len(new_items)

        search_product = {
            'product_id':123,
        }
        response = client.get('/items/',
            json = search_product
        )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['product_id'] == 123

        search_ingredient = {
            'ingredient_id':ingredient_ids['chicken breast'],
        }
        response = client.get('/items/',
            json = search_ingredient
        )

        assert response.status_code == 200
        assert len(response.json) == 2

        search_name = {
            'name':'Kroger'
        }
        response = client.get('/items/',
            json = search_name
        )

        assert response.status_code == 200
        assert len(response.json) == 2


    def test_post_invalid_item(self, app):
        client = app.test_client()

        # missing name
        new_item = {
            'amount':0,
            'product_id':000000,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 422

        # invalid ingredient
        new_item = {
            'name':'Mustard',
            'amount':0,
            'product_id':000000,
            'ingredient_id':1
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 422


    def test_delete_item(self, app):
        client = app.test_client()

        new_item = {
            'name':'Kroger Eggs',
            'amount':12,
            'product_id':123456,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(f'/items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

    def test_delete_invalid_item(self, app):
        client = app.test_client()

        # DELETE requires an etag, so a valid item must exist and be deleted first
        new_item = {
            'name':'Kroger Eggs',
            'amount':12,
            'product_id':123456,
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(f'/items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

        # try to DELETE again
        response = client.delete(f'/items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 404

class TestIngredients:
    def test_get_empty_ingredients(self, app):
        client = app.test_client()

        response = client.get('/ingredients/')
        assert response.status_code == 200
        assert response.json == []

    def test_post_get_ingredient(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'Eggs',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/ingredients/{id}')

        assert response.status_code == 200
        for k,v in new_ingredient.items():
            assert response.json[k] == v

    def test_post_invalid_ingredient(self, app):
        client = app.test_client()

        # missing name
        new_ingredient = {
            
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 422

    def test_delete_ingredient(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'Spinach',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

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
