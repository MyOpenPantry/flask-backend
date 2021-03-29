import pytest, json
from datetime import datetime

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

        '''
        # fake ingredient
        new_item = {
            'name':'eggs'
            'ingredient':'-1'
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_item),
        )

        assert response.status_code == 422
        '''

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
