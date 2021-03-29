import pytest, json
from datetime import datetime


class TestApi:
    def test_get_inventory(self, app):
        client = app.test_client()

        # TODO /v1 is defined as the prefix when initiating the API in create_app(). Is there a way to automatically get that definition here?
        response = client.get('/items/')
        assert response.status_code == 200
        assert response.json == []

    def test_post_inventory(self, app):
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

    def test_post_invalid_inventory(self, app):
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
