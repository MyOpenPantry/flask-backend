import dateutil.parser


class TestItems:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('items/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_nonempty(self, app):
        client = app.test_client()

        item = {
            'name': 'Pineapple',
            'amount': 2,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        response = client.get('items/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_by_id(self, app):
        client = app.test_client()

        item = {
            'name': 'Rice',
            'amount': 1340,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'items/{id}')

        assert response.status_code == 200
        for k, v in item.items():
            assert response.json[k] == v

    def test_get_invalid(self, app):
        client = app.test_client()

        item = {
            'name': 'Pineapple',
            'amount': 2,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'items/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        item = {
            'name': 'Kroger Eggs',
            'amount': 12,
            'productId': 123456,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'items/{id}')

        assert response.status_code == 200
        for k, v in item.items():
            assert response.json[k] == v

    def test_post_invalid(self, app):
        client = app.test_client()

        # missing name
        item_resp = (
            ({'amount': 0, 'productId': 000000}, 422),
            ({
                'name': 'Mustard',
                'amount': 0,
                'productId': 000000,
                'ingredientId': 1
            }, 422),
            ({
                'name': 'Kroger Eggs',
                'amount': 12,
                'productId': 123456,
            }, 201),
            ({
                'name': 'Kroger Eggs',
                'amount': 12,
            }, 422),
            ({
                'name': 'Costco Eggs',
                'amount': 12,
                'productId': 123456,
            }, 422),
        )

        for item, resp in item_resp:
            response = client.post(
                'items/',
                headers={"Content-Type": "application/json"},
                json=item,
            )

            assert response.status_code == resp

    def test_put(self, app):
        client = app.test_client()

        item = {
            'name': 'Peanut Butter',
            'amount': 1,
            'productId': 1000239983223,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']
        updated = response.json['updatedAt']
        etag = response.headers['ETag']

        update_item = {
            'name': 'Peanut Butter',
            'amount': 2,
            'productId': 1000239983223,
        }
        response = client.put(
            f'items/{id}',
            headers={"If-Match": etag},
            json=update_item
        )

        assert response.status_code == 200

        response = client.get(f'items/{id}')

        assert response.status_code == 200
        assert dateutil.parser.parse(response.json['updatedAt']) > dateutil.parser.parse(updated)

    def test_invalid_put(sel, app):
        client = app.test_client()

        item = {
            'name': 'Grape Jelly',
            'amount': 44,
            'productId': 1033239983223,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.put(
            f'items/{id}',
            headers={"If-Match": ''},
            json=item
        )

        assert response.status_code == 428

        # changing read-only field updated
        update_item = {
            'name': 'Grape Jelly',
            'amount': 44,
            'productId': 1033239983223,
            'updatedAt': '2021-03-30T14:55:30.500000'
        }
        response = client.put(
            f'items/{id}',
            headers={"If-Match": etag},
            json=update_item
        )

        assert response.status_code == 422

        # no name
        update_item = {
            'amount': 44,
        }
        response = client.put(
            f'items/{id}',
            headers={"If-Match": etag},
            json=update_item
        )

        assert response.status_code == 422

        # no amount
        update_item = {
            'name': 'Grape Jelly',
        }
        response = client.put(
            f'items/{id}',
            headers={"If-Match": etag},
            json=update_item
        )

        assert response.status_code == 422

    # this also indirectly tests associations since I also want to test querying by ingredientId
    def test_query(self, app):
        client = app.test_client()

        items = (
            {
                'name': 'Kroger Eggs',
                'amount': 12,
                'productId': 123456,
            },
            {
                'name': 'Kroger Chicken Breast',
                'amount': 11,
                'productId': 123,
            },
            {
                'name': 'Costco Chicken Breast',
                'amount': 3,
                'productId': 2323,
            },
            {
                'name': 'Aldi Beef Chuck',
                'amount': 2,
                'productId': 4444,
            },
            {
                'name': 'Bananas',
                'amount': 1,
            },
            {
                'name': 'Apples',
                'amount': 5,
            },
        )

        for item in items:
            response = client.post(
                'items/',
                headers={"Content-Type": "application/json"},
                json=item,
            )
            assert response.status_code == 201

        response = client.get('items/')

        assert response.status_code == 200
        assert len(response.json) == len(items)

        # start of queries
        query_resp = [
            ({'productId': -1}, {'code': 422}),
            ({'productId': 123}, {'code': 200, 'len': 1}),
            ({'productId': 11}, {'code': 200, 'len': 0}),
            ({"name": ''}, {'code': 422}),
            ({"name": 'Kroger'}, {'code': 200, 'len': 2}),
            ({"name": 'Winco'}, {'code': 200, 'len': 0}),
        ]

        for query, resp in query_resp:
            response = client.get(
                'items/',
                headers={'Content-Type': 'application/json'},
                query_string=query
            )

            assert response.status_code == resp['code']
            if resp.get('len', None):
                assert len(response.json) == resp['len']

    def test_delete(self, app):
        client = app.test_client()

        item = {
            'name': 'Kroger Eggs',
            'amount': 12,
            'productId': 123456,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(
            f'items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        # DELETE requires an etag, so a valid item must exist and be deleted first
        item = {
            'name': 'Kroger Eggs',
            'amount': 12,
            'productId': 123456,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.delete(
            f'items/{id}',
            headers={'If-Match': ''}
        )

        assert response.status_code == 428

        response = client.delete(
            f'items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

        # try to DELETE again
        response = client.delete(
            f'items/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 404
