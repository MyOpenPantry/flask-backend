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
