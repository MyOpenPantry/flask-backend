import pytest, json
from datetime import datetime
import dateutil.parser

class TestIngredients:
    def test_query_recipes(self, app):
        pass

    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('/ingredients/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_nonempty(self, app):
        client = app.test_client()

        ingredients = [
            {
                'name':'eggs',
            },
            {
                'name':'peanut butter',
            },
            {
                'name':'chicken tenderloin',
            },
            {
                'name':'cheese',
            },
        ] 

        for ingredient in ingredients:
            response = client.post('/ingredients/', 
                headers = {"Content-Type": "application/json"},
                data = json.dumps(ingredient),
            )

            assert response.status_code == 201

        response = client.get('/ingredients/')

        assert response.status_code == 200
        assert len(response.json) == len(ingredients)

    def test_get(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'berry',
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        for k,v in new_ingredient.items():
            assert response.json[k] == v

    def test_get_invalid(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'potato',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/items/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
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

    def test_post_invalid(self, app):
        client = app.test_client()

        # missing name
        new_ingredient = {}

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 422

    def test_post_existing(self, app):
        pass

    def test_put(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'butter',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        update_item = {
            'name':'Butter',
        }
        response = client.put(f'/ingredients/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 200

        response = client.get(f'/ingredients/{id}') 

        assert response.status_code == 200

    def test_invalid_put(self, app):
        client = app.test_client()

        new_ingredient = {
            'name':'butter',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(new_ingredient),
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # missing required 'name'
        update_item = {}
        response = client.put(f'/ingredients/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 422

    def test_query(self, app):
        pass

    def test_delete(self, app):
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

    def test_delete_invalid(self, app):
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

        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 404
