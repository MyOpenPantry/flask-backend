import pytest, json

class TestRecipeTags:
    def test_link_get(self, app):
        client = app.test_client()

        recipe = {
            'name':'Arugula Salad',
            'steps': 'add all ingredients to bowl and toss'
        }

        tags = [
            {
                'name':'arugula'
            },
            {
                'name':'vegetarian'
            },
            {
                'name':'salad'
            }
        ]

        response = client.post('recipes/',
            headers = {'Content-Type':'application/json'},
            json = recipe
        )

        assert response.status_code == 201

        recipe_id = response.json['id']

        tag_ids = []
        for tag in tags:
            response = client.post('tags/',
                headers = {'Content-Type':'application/json'},
                json = tag
            )

            assert response.status_code == 201

            tag_ids.append(response.json['id'])

        # add tags to the recipe from the recipe side
        response = client.post(f'recipes/{recipe_id}/tags',
            headers = {'Content-Type':'application/json'},
            json = {'tag_ids': tag_ids[1:]}
        )

        assert response.status_code == 204

        # add tags to the recipe from the tag side
        response = client.post(f'tags/{tag_ids[0]}/recipes',
            headers = {'Content-Type':'application/json'},
            json = {'recipe_ids': [recipe_id]}
        )

        assert response.status_code == 204

        # verify the association from recipes/id/tags
        response = client.get(f'recipes/{recipe_id}/tags')

        assert response.status_code == 200
        assert len(response.json) == len(tags)

        # verify the association shows up in /tags/id/recipes
        for tag_id in tag_ids:
            response = client.get(f'tags/{tag_id}/recipes')

            assert response.status_code == 200
            assert len(response.json) == 1

    def test_unlink(self, app):
        client = app.test_client()

        recipe = {
            'name':'Arugula Salad',
            'steps': 'add all ingredients to bowl and toss'
        }

        tags = [
            {
                'name':'arugula'
            },
            {
                'name':'vegetarian'
            },
            {
                'name':'salad'
            }
        ]

        response = client.post('recipes/',
            headers = {'Content-Type':'application/json'},
            json = recipe
        )

        assert response.status_code == 201

        recipe_id = response.json['id']
        recipe_etag = response.headers['ETag']

        tag_ids = []
        tag_etags = []
        for tag in tags:
            response = client.post('tags/',
                headers = {'Content-Type':'application/json'},
                json = tag
            )

            assert response.status_code == 201

            tag_ids.append(response.json['id'])
            tag_etags.append(response.headers['ETag'])

        # add first tag to recipe from recipes/id/tags
        response = client.post(f'recipes/{recipe_id}/tags',
            headers = {'Content-Type':'application/json'},
            json = {'tag_ids': tag_ids[1:]}
        )

        assert response.status_code == 204

        # do the same with the other tag, but by adding the recipe to the tag from tags/id/recipes
        response = client.post(f'tags/{tag_ids[0]}/recipes',
            headers = {'Content-Type':'application/json'},
            json = {'recipe_ids': [recipe_id]}
        )

        assert response.status_code == 204

        # make sure both tags are returned
        response = client.get(f'recipes/{recipe_id}/tags')

        assert response.status_code == 200
        assert len(response.json) == len(tags)

        # delete the first tag from recipes/id/tags
        response = client.delete(f'recipes/{recipe_id}/tags/{tag_ids[0]}',
            headers = {'If-Match': recipe_etag},
        )

        assert response.status_code == 204

        response = client.get(f'recipes/{recipe_id}/tags')

        assert response.status_code == 200
        assert len(response.json) == 2

        # delete the second tag from tags/id/recipes
        response = client.delete(f'tags/{tag_ids[1]}/recipes/{recipe_id}',
            headers = {'If-Match': tag_etags[1]},
        )

        assert response.status_code == 204

        response1 = client.get(f'recipes/{recipe_id}/tags')
        response2 = client.get(f'tags/{tag_ids[1]}/recipes')

        assert response1.status_code == response2.status_code == 200
        assert len(response1.json) == 1
        assert len(response2.json) == 0

    def test_link_invalid(self, app):
        client = app.test_client()

        recipe = {
            'name':'Arugula Salad',
            'steps': 'add all ingredients to bowl and toss'
        }

        tags = [
            {
                'name':'arugula'
            },
            {
                'name':'vegetarian'
            },
        ]

        response = client.post('recipes/',
            headers = {'Content-Type':'application/json'},
            json = recipe
        )

        assert response.status_code == 201

        recipe_id = response.json['id']

        tag_ids = []
        for tag in tags:
            response = client.post('tags/',
                headers = {'Content-Type':'application/json'},
                json = tag
            )

            assert response.status_code == 201

            tag_ids.append(response.json['id'])

        # invalid recipe, valid tag
        response = client.post(f'recipes/{recipe_id+1}/tags',
            headers = {'Content-Type':'application/json'},
            json = {'tag_ids': [tag_ids[0]]}
        )

        assert response.status_code == 404

        # valid recipe, invalid tag
        response = client.post(f'recipes/{recipe_id}/tags',
            headers = {'Content-Type':'application/json'},
            json = {'tag_ids': [tag_ids[1] + 1]}
        )

        assert response.status_code == 404

        # valid tag, invalid recipe
        response = client.post(f'tags/{tag_ids[0]}/recipes',
            headers = {'Content-Type':'application/json'},
            json = {'recipe_ids': [recipe_id + 1]}
        )

        assert response.status_code == 404

        # invalid tag, valid recipe
        response = client.post(f'tags/{tag_ids[1] + 1}/recipes',
            headers = {'Content-Type':'application/json'},
            json = {'recipe_ids': [recipe_id]}
        )

        assert response.status_code == 404

    def test_get_empty(self, app):
        client = app.test_client()

        recipe = {
            'name':'Arugula Salad',
            'steps': 'add all ingredients to bowl and toss'
        }

        tags = [
            {
                'name':'arugula'
            },
            {
                'name':'vegetarian'
            },
        ]

        response = client.post('recipes/',
            headers = {'Content-Type':'application/json'},
            json = recipe
        )

        assert response.status_code == 201

        recipe_id = response.json['id']

        tag_ids = []
        for tag in tags:
            response = client.post('tags/',
                headers = {'Content-Type':'application/json'},
                json = tag
            )

            assert response.status_code == 201

            tag_ids.append(response.json['id'])

        # make sure both are now empty
        response = client.get(f'recipes/{recipe_id}/tags')

        assert response.status_code == 200
        assert len(response.json) == 0

        for tag_id in tag_ids:
            response2 = client.get(f'tags/{tag_id}/recipes')

            assert response.status_code == 200
            assert len(response.json) == 0
