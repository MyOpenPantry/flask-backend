import pytest, json
from datetime import datetime
import dateutil.parser

class TestTags:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('/tags/')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_nonempty(self, app):
        client = app.test_client()

        tag = {
            'name':'greek',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(tag),
        )

        response = client.get('/tags/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_item(self, app):
        client = app.test_client()

        tag = {
            'name':'chicken',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            data = json.dumps(tag),
        )

        id = response.json['id']

        response = client.get(f'/tags/{id}')

        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == tag['name']

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
