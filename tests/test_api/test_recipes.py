import pytest, json

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
            json = recipe,
        )

        response = client.get('/recipes/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_by_id(self, app):
        client = app.test_client()

        recipe = {
            'name':'Jerk Chicken',
            'notes':'always use the grill',
            'rating':9,
            'steps':'1 2 3 4',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        id = response.json['id']

        response = client.get(f'/recipes/{id}')
        assert response.status_code == 200
        for k in recipe.keys():
            assert response.json[k] == recipe[k]

    def test_get_invalid(self, app):
        client = app.test_client()

        recipe = {
            'name':'Lasagna Salad',
            'notes':'',
            'rating':7,
            'steps':'the lazy brown fox jumped over the quick dog',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        id = response.json['id']

        response = client.get(f'/recipes/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        recipe = {
            'name':'Roasted Broccoli',
            'notes':'add whatever spices you want',
            'rating':999,
            'steps':'Preheat oven to 400. Coat broccoli florets in garlic, salt, and pepper. Put broccoli in single layer on baking tray in oven for 20 minutes, stir, and leave in for 10 more minutes',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201
        
        for k in recipe.keys():
            assert response.json[k] == recipe[k]

    def test_post_invalid(self, app):
        client = app.test_client()

        invalid_recipes = [
            # no name
            {
                'notes':'add whatever spices you want',
                'rating':999,
                'steps':'Preheat oven to 400. Coat broccoli florets in garlic, salt, and pepper. Put broccoli in single layer on baking tray in oven for 20 minutes, stir, and leave in for 10 more minutes',
            },
            # non-int rating
            {
            'name':'Roasted Broccoli',
            'notes':'add whatever spices you want',
            'rating':'asdf',
            'steps':'Preheat oven to 400. Coat broccoli florets in garlic, salt, and pepper. Put broccoli in single layer on baking tray in oven for 20 minutes, stir, and leave in for 10 more minutes',
            },
            # no steps
            {
                'name':'Roasted Broccoli',
                'notes':'add whatever spices you want',
                'rating':999,
            },
            # empty
            {

            }
        ]

        for recipe in invalid_recipes:
            response = client.post('/recipes/', 
                headers = {"Content-Type": "application/json"},
                json = recipe,
            )

            assert response.status_code == 422

    def test_post_existing(self, app):
        client = app.test_client()

        recipe = {
            'name':'Baked Sweet Potato',
            'notes':'jerk seasoning works well with this',
            'rating':10,
            'steps':'test',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 422

    def test_put(self, app):
        client = app.test_client()

        recipe = {
            'name':'Cheescak',
            'steps':'steps here',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        recipe['name'] = 'Cheesecake'
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": etag},
            json = recipe,
        )

        assert response.status_code == 200

    def test_invalid_put(self, app):
        client = app.test_client()

        recipe = {
            'name':'Marinara',
            'notes':'italian sauce',
            'rating':1,
            'steps':'steps',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": ''},
            json = recipe,
        )

        assert response.status_code == 428

        # no recipe name
        del recipe['name']
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": etag},
            json = recipe,
        )

        assert response.status_code == 422

        # no recipe steps
        recipe['name'] = 'Marinara'
        del recipe['steps']
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": etag},
            json = recipe,
        )

        assert response.status_code == 422

        # invalid rating #1
        recipe['steps'] = 'test'
        recipe['rating'] = -1
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": etag},
            json = recipe,
        )

        assert response.status_code == 422

        # invalid rating #2
        recipe['rating'] = 'not an int'
        response = client.put(f'/recipes/{id}', 
            headers = {"If-Match": etag},
            json = recipe,
        )

        assert response.status_code == 422

    # TODO clean this mess
    def test_query(self, app):
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

            r_ids = {'recipeIds': [recipe_ids[r_name]]}

            response = client.post(f'/tags/{t_id}/recipes', 
                headers = {"Content-Type":"application/json"},
                json = r_ids
            )

            assert response.status_code == 204

        ingredients = [
            {
                'name':'Black Beans',
            },
            {
                'name':'Pineapple',
            },
            {
                'name':'Rice',
            },
            {
                'name':'Chicken Breast',
            },
            {
                'name':'Not Used',
            },
            {
                'name':'Tomato',
            },
        ]

        ingredient_info = dict()

        for ingredient in ingredients:
            response = client.post('/ingredients/', 
                headers = {"Content-Type":"application/json"},
                json = {'name':ingredient['name']}
            )

            assert response.status_code == 201

            ingredient_info[ingredient['name']] = (response.json['id'], response.headers['ETag'])

        associations = [
            ['Black Beans','Black Bean Pineapple Salsa', 2, '15oz cans'],
            ['Pineapple','Black Bean Pineapple Salsa', 1, 'pineapple'],
            ['Tomato','Fruit Salad', 6, 'tomato'],
            ['Chicken Breast','Chicken Salad', 2, 'lbs'],
            ['Rice','Red Beans and Rice', 2, 'cups'],
            ['Tomato','Black Bean Pineapple Salsa', 2, 'tomato'],
        ]

        for i_name, r_name, amount, unit in associations:
            r_id = recipe_ids[r_name]
            i_id, _ = ingredient_info[i_name]

            response = client.post(f'/recipes/{r_id}/ingredients',
                headers = {"Content-Type":"application/json"},
                json = {'recipeIngredients': [{'ingredientId': i_id, 'amount':amount, 'unit':unit}]}
            )

            assert response.status_code == 204

        # recipe name
        query = {'names':['Black Bean', 'Salad']}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 3

        query = {'names':[]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert response.status_code == 422

        query = {'names':['Bean']}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 2

        query = {'tagIds':[tag_info['creole'][0], tag_info['vegetarian'][0]]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 4

        query = {'tagIds':[tag_info['creole'][0], tag_info['vegetarian'][0]]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 4

        query = {'tagIds':[]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert response.status_code == 422

        query = {'ingredientIds':[ingredient_info['Black Beans'][0], ingredient_info['Tomato'][0]]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 2

        query = {'ingredientIds':[ingredient_info['Not Used'][0]]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert len(response.json) == 0

        query = {'ingredientIds':[]}
        response = client.get('recipes/',
            headers = {'Content-Type':'application/json'},
            json = query
        )

        assert response.status_code == 422

    def test_delete(self, app):
        client = app.test_client()

        recipe = {
            'name':'Roasted Brussel Sprouts',
            'notes':'add whatever spices you want',
            'rating':99999,
            'steps':'hello',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201
        
        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(f'/recipes/{id}',
            headers = {'If-Match': etag}
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        recipe = {
            'name':'Roasted Brussel Sprouts',
            'notes':'add whatever spices you want',
            'rating':99999,
            'steps':'hello',
        }

        response = client.post('/recipes/', 
            headers = {"Content-Type": "application/json"},
            json = recipe,
        )

        assert response.status_code == 201
        
        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.delete(f'/recipes/{id}',
            headers = {'If-Match': ''}
        )

        assert response.status_code == 428

        response = client.delete(f'/recipes/{id}',
            headers = {'If-Match': etag}
        )

        assert response.status_code == 204

        response = client.delete(f'/recipes/{id}',
            headers = {'If-Match': etag}
        )

        assert response.status_code == 404
