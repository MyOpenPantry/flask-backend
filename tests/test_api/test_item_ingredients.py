
class TestItemIngredients:
    def test_link_get(self, app):
        client = app.test_client()

        # create an item with no ingredient id set
        item1 = {
            'name': 'Kroger Chicken Thighs',
            'amount': 6,
            'productId': 1111111111111,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item1,
        )

        assert response.status_code == 201

        item1_id = response.json['id']
        item1_etag = response.headers['ETag']

        # create an ingredient
        ingredient = {
            'name': 'chicken thighs',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        ingredient_id = response.json['id']

        # create another item, this time with the newly created ingredient id
        item2 = {
            'name': 'Costco Chicken Thighs',
            'amount': 2,
            'productId': 2222222222222,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item2,
        )

        assert response.status_code == 201

        # update the first item to use the ingredient
        item1['ingredientId'] = ingredient_id
        response = client.put(
            f'items/{item1_id}',
            headers={'If-Match': item1_etag},
            json=item1,
        )

        assert response.status_code == 200
        assert response.json['ingredient']['id'] == ingredient_id

        response = client.get(f'items/{item1_id}/ingredient')

        assert response.status_code == 200
        assert response.json['id'] == ingredient_id

        response = client.get(f'ingredients/{ingredient_id}/items')

        assert response.status_code == 200
        assert response.json[0]['id'] == item1_id

        # create another item, this time with the newly created ingredient id
        item3 = {
            'name': 'Aldi Chicken Thighs',
            'amount': 46,
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item3,
        )

        assert response.status_code == 201

    def test_unlink(self, app):
        client = app.test_client()

        ingredient = {
            'name': 'vegetable',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201

        ingredient_id = response.json['id']

        item = {
            'name': 'Asparagus',
            'amount': 2,
            'productId': 54,
            'ingredientId': ingredient_id
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # remove the ingredient association via put on items/id
        del item['ingredientId']
        response = client.put(
            f'items/{id}',
            headers={'If-Match': etag},
            json=item
        )

        assert response.status_code == 200
        assert response.json.get('ingredientId', None) is None

        # check that the ingredient wasn't deleted
        response = client.get(f'ingredients/{ingredient_id}')

        assert response.status_code == 200

        # obtain the new etag for the item
        response = client.get(f'items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # Add the ingredient back so deleting from items/id/ingredient can be tested
        item['ingredientId'] = ingredient_id
        response = client.put(
            f'items/{id}',
            headers={'If-Match': etag},
            json=item
        )

        assert response.status_code == 200
        assert response.json['ingredient']['id'] == ingredient_id

        # obtain the new etag for the item
        response = client.get(f'items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # delete the association from items/id/ingredient this time
        response = client.delete(
            f'items/{id}/ingredient',
            headers={'If-Match': etag},
        )

        assert response.status_code == 204

        # check that the ingredient wasn't deleted
        response = client.get(f'ingredients/{ingredient_id}')

        assert response.status_code == 200

        # obtain the new etag for the item
        response = client.get(f'items/{id}')

        assert response.status_code == 200
        etag = response.headers['ETag']

        # Add the ingredient back so deleting from items/id/ingredient can be tested
        item['ingredientId'] = ingredient_id
        response = client.put(
            f'items/{id}',
            headers={'If-Match': etag},
            json=item
        )

        assert response.status_code == 200
        assert response.json['ingredient']['id'] == ingredient_id

    # sqlite doesn't enforce foreign key constraints by default so test that it is enabled
    def test_link_invalid(self, app):
        client = app.test_client()

        item = {
            'name': 'Rutabaga',
            'amount': 9999,
            'productId': 4412,
            'ingredientId': 1
        }

        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 422

        # remove the invalid ingredientId so there is a real item to work with
        del item['ingredientId']
        response = client.post(
            'items/',
            headers={"Content-Type": "application/json"},
            json=item,
        )

        assert response.status_code == 201

        # create an ingredient
        ingredient = {
            'name': 'rutabaga',
        }

        response = client.post(
            'ingredients/',
            headers={"Content-Type": "application/json"},
            json=ingredient,
        )

        assert response.status_code == 201
