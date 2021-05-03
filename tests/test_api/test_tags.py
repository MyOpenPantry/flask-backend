
class TestTags:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('tags/')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_nonempty(self, app):
        client = app.test_client()

        tag = {
            'name': 'greek',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        response = client.get('tags/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_by_id(self, app):
        client = app.test_client()

        tag = {
            'name': 'chicken',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        id = response.json['id']

        response = client.get(f'tags/{id}')

        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == tag['name']

    def test_get_invalid(self, app):
        client = app.test_client()

        tag = {
            'name': 'beef',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        id = response.json['id']

        response = client.get(f'tags/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        tag = {
            'name': 'chicken',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

    def test_post_invalid(self, app):
        client = app.test_client()

        tag = {}

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 422

    def test_post_existing(self, app):
        client = app.test_client()

        tag = {
            'name': 'chicken',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        id = response.json['id']

        response = client.get(f'tags/{id}')

        assert response.status_code == 200

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 422

    def test_put(self, app):
        client = app.test_client()

        tag = {
            'name': 'vegetaria',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        tag['name'] = 'vegetarian'

        response = client.put(
            f'tags/{id}',
            headers={"If-Match": etag},
            json=tag,
        )

        assert response.status_code == 200
        assert response.json['name'] == tag['name']

    def test_invalid_put(self, app):
        client = app.test_client()

        tag = {
            'name': 'vegetaria',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        # no etag
        response = client.put(
            f'tags/{id}',
            headers={"If-Match": ''},
            json=tag,
        )

        assert response.status_code == 428

        # no name
        del tag['name']
        response = client.put(
            f'tags/{id}',
            headers={"If-Match": etag},
            json=tag,
        )

        assert response.status_code == 422

    def test_query(self, app):
        client = app.test_client()

        tags = [
            {
                'name': 'creole'
            },
            {
                'name': 'vegetarian'
            },
            {
                'name': 'side'
            },
            {
                'name': 'meat'
            },
            {
                'name': 'chicken thigh'
            },
            {
                'name': 'chicken breast'
            }
        ]

        for tag in tags:
            response = client.post(
                'tags/',
                headers={"Content-Type": "application/json"},
                json=tag,
            )

            assert response.status_code == 201

        # start of queries
        query_resp = [
            ({'name': ''}, {'code': 422}),
            ({'name': 'meat'}, {'code': 200, 'len': 1}),
            ({'name': 'chicken'}, {'code': 200, 'len': 2}),
            ({'name': 'no such tag'}, {'code': 200, 'len': 0}),
        ]

        for query, resp in query_resp:
            response = client.get(
                'tags/',
                headers={'Content-Type': 'application/json'},
                query_string=query
            )

            print(response.json)
            assert response.status_code == resp['code']
            if resp.get('len', None):
                assert len(response.json) == resp['len']

    def test_delete(self, app):
        client = app.test_client()

        tag = {
            'name': 'vegetaria',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        response = client.delete(
            f'tags/{id}',
            headers={"If-Match": etag},
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        tag = {
            'name': 'savory',
        }

        response = client.post(
            'tags/',
            headers={"Content-Type": "application/json"},
            json=tag,
        )

        assert response.status_code == 201

        etag = response.headers['ETag']
        id = response.json['id']

        # no etag
        response = client.delete(
            f'tags/{id}',
            headers={"If-Match": ''},
        )

        assert response.status_code == 428

        response = client.delete(
            f'tags/{id}',
            headers={"If-Match": etag},
        )

        assert response.status_code == 204

        response = client.delete(
            f'tags/{id}',
            headers={"If-Match": etag},
        )

        assert response.status_code == 404
