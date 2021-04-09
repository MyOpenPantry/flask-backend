import pytest, json

class TestIngredients:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('/ingredients/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_nonempty(self, app):
        client = app.test_client()

        ingredients = [
            {
                'name':'eggs',
            },
            {
                'name':'peanut butter',
            },
            {
                'name':'chicken tenderloin',
            },
            {
                'name':'cheese',
            },
        ] 

        for ingredient in ingredients:
            response = client.post('/ingredients/', 
                headers = {"Content-Type": "application/json"},
                json = ingredient,
            )

            assert response.status_code == 201

        response = client.get('/ingredients/')

        assert response.status_code == 200
        assert len(response.json) == len(ingredients)

    def test_get_by_id(self, app):
        client = app.test_client()

        ingredient = {
            'name':'berry',
        }

        response = client.post('/items/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/items/{id}')

        assert response.status_code == 200
        for k,v in ingredient.items():
            assert response.json[k] == v

    def test_get_invalid(self, app):
        client = app.test_client()

        ingredient = {
            'name':'potato',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/items/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        ingredient = {
            'name':'Eggs',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/ingredients/{id}')

        assert response.status_code == 200
        for k,v in ingredient.items():
            assert response.json[k] == v

    def test_post_invalid(self, app):
        client = app.test_client()

        # missing name
        ingredient = {}

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 422

    def test_post_existing(self, app):
        client = app.test_client()

        ingredient = {
            'name':'Eggs',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']

        response = client.get(f'/ingredients/{id}')

        assert response.status_code == 200
        for k,v in ingredient.items():
            assert response.json[k] == v

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 422

    def test_put(self, app):
        client = app.test_client()

        ingredient = {
            'name':'butter',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        update_item = {
            'name':'Butter',
        }
        response = client.put(f'/ingredients/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 200

        response = client.get(f'/ingredients/{id}') 

        assert response.status_code == 200

    def test_invalid_put(self, app):
        client = app.test_client()

        ingredient = {
            'name':'butter',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.put(f'/ingredients/{id}',
            headers = {"If-Match": ''},
            json = ingredient
        )

        assert response.status_code == 428

        # missing required 'name'
        update_item = {}
        response = client.put(f'/ingredients/{id}',
            headers = {"If-Match": etag},
            json = update_item
        )

        assert response.status_code == 422

    def test_query(self, app):
        client = app.test_client()

        ingredients = [
            {
                'name':'Black Beans',
            },
            {
                'name':'Red Beans',
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

        associations = [
            ['Black Beans','Black Bean Pineapple Salsa', 2.0, '15oz cans'],
            ['Pineapple','Black Bean Pineapple Salsa', 1.0, 'pineapple'],
            ['Tomato','Fruit Salad', 0.5, 'tomato'],
            ['Chicken Breast','Chicken Salad', 2.0, 'lbs'],
            ['Rice','Red Beans and Rice', 2.0, 'cups'],
            ['Tomato','Black Bean Pineapple Salsa', 2.0, 'tomato'],
        ]

        for i_name, r_name, amount, unit in associations:
            r_id = recipe_ids[r_name]
            i_id, _ = ingredient_info[i_name]

            response = client.post(f'/recipes/{r_id}/ingredients',
                headers = {"Content-Type":"application/json"},
                json = {'recipe_ingredients': [{'ingredient_id': i_id, 'amount':amount, 'unit':unit}]}
            )

            assert response.status_code == 204

        item_ids = dict()
        items = [
            {
                'name':'Pineapple',
                'amount':3,
                'product_id':123456,
                'ingredient_id':ingredient_info['Pineapple'][0]
            },
            {
                'name':'No ingredient',
                'amount':0,
            },
            {
                'name':'Simple Truth Black Beans',
                'amount':4,
                'product_id':44121212,
                'ingredient_id':ingredient_info['Black Beans'][0]
            },
            {
                'name':'Walmart Black Beans',
                'amount':4,
                'product_id':22121212,
                'ingredient_id':ingredient_info['Black Beans'][0]
            },
            {
                'name':'Rice',
                'amount':1,
                'product_id':777,
                'ingredient_id':ingredient_info['Rice'][0]
            },
            {
                'name':'Tomato',
                'amount':6,
                'product_id':111222333,
                'ingredient_id':ingredient_info['Tomato'][0]
            },
        ]

        for item in items:
            response = client.post('/items/', 
                headers = {"Content-Type": "application/json"},
                json = item,
            )

            assert response.status_code == 201

            item_ids[item['name']] = response.json['id']

        # start of queries

        query_resp = [
            [{"names":['Bean', 'Tomato']}, {'code': 200, 'len':3}],
            [{"names":['Tomato']}, {'code': 200, 'len':1}],
            [{"names":[]}, {'code': 422}],
            [{"recipe_ids":[recipe_ids['Chicken Salad'], recipe_ids['Black Bean Pineapple Salsa']]}, {'code': 200, 'len':4}],
            [{"recipe_ids":[recipe_ids['Red Beans and Rice']]}, {'code': 200, 'len':1}],
            [{"recipe_ids":[]}, {'code': 422}],
            [{"item_ids":[item_ids['Pineapple']]}, {'code': 200, 'len':1}],
            [{"item_ids":[item_ids['No ingredient']]}, {'code': 200, 'len':0}],
            [{"item_ids":[item_ids['Simple Truth Black Beans'], item_ids['Walmart Black Beans']]}, {'code': 200, 'len':1}],
            [{"item_ids":[]}, {'code': 422}],
        ]

        for query, resp in query_resp:
            response = client.get(
                '/ingredients/',
                headers = {'Content-Type':'application/json'},
                json = query
            )

            print(query)
            assert response.status_code == resp['code']

            if resp.get('len', None) is not None:
                assert len(response.json) == resp['len']

    def test_delete(self, app):
        client = app.test_client()

        ingredient = {
            'name':'Spinach',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        ingredient = {
            'name':'Spinach',
        }

        response = client.post('/ingredients/', 
            headers = {"Content-Type": "application/json"},
            json = ingredient,
        )

        assert response.status_code == 201

        id = response.json['id']
        etag = response.headers['ETag']

        # no etag
        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': ''}
        )

        assert response.status_code == 428

        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 204

        response = client.delete(f'/ingredients/{id}',
            headers={'If-Match': etag}
        )

        assert response.status_code == 404
