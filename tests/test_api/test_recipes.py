import pytest, json
from datetime import datetime
import dateutil.parser

class TestRecipes:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('/recipes/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_nonempty(self, app):
        client = app.test_client()

        recipe = {
            'name':'Black Bean Pineapple Salsa',
            'notes':'Goes well with jerk chicken and rice',
            'rating':10,
            'steps':'put all ingredients in the bowl and stir',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(recipe),
        )

        response = client.get('/recipes/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_item(self, app):
        pass

    def test_get_invalid(self, app):
        pass

    def test_post(self, app):
        pass

    def test_post_invalid(self, app):
        pass

    def test_post_existing(self, app):
        pass

    def test_put(self, app):
        pass

    def test_invalid_put(self, app):
        pass

    def test_query(self, app):
        pass

    def test_delete(self, app):
        pass

    def test_delete_invalid(self, app):
        pass
