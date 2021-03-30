import pytest, json

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
