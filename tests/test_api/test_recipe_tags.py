import pytest, json

class TestRecipeTags:
    def test_link(self, app):
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
        recipe_etag = response.headers['ETag']

        tag_ids = []
        for tag in tags:
            response = client.post('tags/',
                headers = {'Content-Type':'application/json'},
                json = tag
            )

            assert response.status_code == 201

            tag_ids.append(response.json['id'])

        response = client.post(f'recipes/{recipe_id}/tags',
            headers = {'If-Match': recipe_etag},
            json = {'tag_ids': tag_ids}
        )

        assert response.status_code == 204

        response = client.get(f'recipes/{recipe_id}/tags')

        assert len(response.json) == len(tags) 

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
            headers = {'If-Match':recipe_etag},
            json = {'tag_ids': [tag_ids[0]]}
        )
        
        assert response.status_code == 204

        # do the same with the other tag, but by adding the recipe to the tag from tags/id/recipes
        response = client.post(f'tags/{tag_ids[1]}/recipes',
            headers = {'If-Match':tag_etags[1]},
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
        assert len(response.json) == 1

        # delete the second tag from tags/id/recipes
        response = client.delete(f'tags/{tag_ids[1]}/recipes/{recipe_id}',
            headers = {'If-Match': tag_etags[1]},
        )

        assert response.status_code == 204

        # make sure both are now empty
        response1 = client.get(f'recipes/{recipe_id}/tags')
        response2 = client.get(f'tags/{tag_ids[1]}/recipes')

        assert len(response1.json) == 0
        assert len(response2.json) == 0

    def test_link_invalid(self, app):
        pass

    def test_get(self, app):
        pass

    def test_get_empty(self, app):
        pass

    def test_get_tags_from_recipe(self, app):
        pass

    def test_get_recipes_from_tag(self, app):
        pass

        client = app.test_client()

        recipe_ids = dict()

        recipes = [
            {
                'name':'Black Bean Pineapple Salsa',
                'notes':'Goes well with jerk chicken and rice',
                'rating':10,
                'steps':'put all ingredients in the bowl and stir',
            },
            {
                'name':'Red Beans and Rice',
                'notes':'',
                'steps':'lorem ipsum',
            },
            {
                'name':'Chicken Salad',
                'notes':'just a test',
                'steps':'nothing.',
                'rating':0,
            },
            {
                'name':'Cauliflower Taco',
                'notes':'family loves them',
                'steps':'just do it',
                'rating':999,
            },
            {
                'name':'Fruit Salad',
                'notes':'good for picnics',
                'steps':'put all the fruit in a bowl',
            },
            {
                'name':'Beef Stew',
                'notes':'cold day food',
                'steps':'I really need to find an actual recipe to put into the steps for this',
            },
        ]

        for recipe in recipes:
            response = client.post('/recipes/', 
                headers = {"Content-Type": "application/json"},
                json = recipe,
            )

            assert response.status_code == 201

            recipe_ids[response.json['name']] = response.json['id']

        tags = [
            {
                'name':'creole'
            },
            {
                'name':'vegetarian'
            },
            {
                'name':'side'
            },
            {
                'name':'meat'
            },
        ]

        tag_info = dict()

        for tag in tags:
            response = client.post('/tags/', 
                headers = {"Content-Type": "application/json"},
                json = tag,
            )

            assert response.status_code == 201
            tag_info[response.json['name']] = (response.json['id'], response.headers['ETag'])

        # TODO this can be done "better", but its late and I just ultimately want to test the endpoint
        associations = [
            ['Black Bean Pineapple Salsa','vegetarian'],
            ['Cauliflower Taco','vegetarian'],
            ['Fruit Salad','vegetarian'],
            ['Chicken Salad','meat'],
            ['Beef Stew','meat'],
            ['Red Beans and Rice','creole'],
            ['Red Beans and Rice','meat'],
            ['Red Beans and Rice','vegetarian'],
            ['Fruit Salad','side'],
            ['Black Bean Pineapple Salsa','side'],
            ['Chicken Salad','side'],
        ]

        for r_name, t_name in associations:
            t_id, t_etag = tag_info[t_name]

            r_ids = {'recipe_ids': [recipe_ids[r_name]]}

            response = client.post(f'/tags/{t_id}/recipes', 
                headers = {"Content-Type":"application/json"},
                json = r_ids
            )

            assert response.status_code == 204

        # tag name
        query = {'names':['side', 'vegetarian']}
        response = client.get('tags/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 2

        query = {'names':[]}
        response = client.get('tags/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == len(tags)

        query = {'names':['meat']}
        response = client.get('tags/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 1