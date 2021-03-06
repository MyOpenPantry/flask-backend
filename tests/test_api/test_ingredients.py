
class TestIngredients:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('ingredients/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_nonempty(self, app):
        client = app.test_client()

        ingredients = [
            {
                'name': 'eggs',
            },
            {
                'name': 'peanut butter',
            },
            {
                'name': 'chicken tenderloin',
            },
            {
                'name': 'cheese',
            },
        ]

        for ingredient in ingredients:
            response = client.post(
                'ingredients/',
                headers={"Content-Type": "application/json"},
                json=ingredient,
            )

            assert response.status_code == 201

        response = client.get('ingredients/')

        assert response.status_code == 200
        assert len(response.json) == len(ingredients)

    def test_get_by_id(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'berry',
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'items/{id}')

        assert response.status_code == 200
        for k, v in ingredient.items():
            assert response.json[k] == v

    def test_get_invalid(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'potato',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'items/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'Eggs',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'ingredients/{id}')

        assert response.status_code == 200
        for k, v in ingredient.items():
            assert response.json[k] == v

        # try again to test name integrity
        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 422

    def test_post_invalid(self, app):
        client = app.test_client()

        # missing name
        ingredient = {}

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 422

    def test_post_existing(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'Eggs',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'ingredients/{id}')

        assert response.status_code == 200
        for k, v in ingredient.items():
            assert response.json[k] == v

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 422

    def test_put(self, app):
        client = app.test_client()

        ingredients = (
            {'name': 'butter'},
            {'name': 'cheese'}
        )

        ingredient_info = {}
        etags = {}

        for ingredient in ingredients:
            response = client.post(
                'ingredients/',
                headers={"Content-Type": "application/json"},
                json=ingredient,
            )

            assert response.status_code == 201

            ingredient_info[response.json['name']] = response.json
            etags[response.json['name']] = response.headers['ETag']

        # try to change butter to cheese to check name integrity
        update_item = {
            'name': 'cheese',
        }
        response = client.put(
            f'ingredients/{ingredient_info["butter"]["id"]}',
            headers={'If-Match': etags['butter']},
            json=update_item
        )

        assert response.status_code == 422

        # capitalize butter to try a valid name change
        update_item = {
            'name': 'Butter',
        }
        response = client.put(
            f'ingredients/{ingredient_info["butter"]["id"]}',
            headers={'If-Match': etags['butter']},
            json=update_item
        )

        assert response.status_code == 200

    def test_invalid_put(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'butter',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.put(
            f'ingredients/{id}',
            headers={'If-Match': ''},
            json=ingredient
        )

        assert response.status_code == 428

        # missing required 'name'
        update_item = {}
        response = client.put(
            f'ingredients/{id}',
            headers={'If-Match': etag},
            json=update_item
        )

        assert response.status_code == 422

    def test_query(self, app):
        client = app.test_client()

        ingredients = [
            {'name': 'Black Beans'},
            {'name': 'Red Beans'},
            {'name': 'Pineapple'},
            {'name': 'Rice'},
            {'name': 'Chicken Breast'},
            {'name': 'Not Used'},
            {'name': 'Tomato'},
        ]

        ingredient_info = dict()

        for ingredient in ingredients:
            response = client.post(
                'ingredients/',
                headers={"Content-Type": "application/json"},
                json=ingredient
            )

            assert response.status_code == 201

            ingredient_info[ingredient['name']] = (response.json['id'], response.headers['ETag'])

        # start of queries
        query_resp = [
            ({"name": 'Bean'}, {'code': 200, 'len': 2}),
            ({"name": 'Tomato'}, {'code': 200, 'len': 1}),
            ({"name": ''}, {'code': 422}),
        ]

        for query, resp in query_resp:
            response = client.get(
                'ingredients/',
                headers={'Content-Type': 'application/json'},
                query_string=query
            )

            assert response.status_code == resp['code']
            if resp.get('len', None):
                assert len(response.json) == resp['len']

    def test_delete(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'Spinach',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(
            f'ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'Spinach',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.delete(
            f'ingredients/{id}',
            headers={'If-Match': ''}
        )

        assert response.status_code == 428

        response = client.delete(
            f'ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

        response = client.delete(
            f'ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 404
