import pytest

class TestIngredientRecipes:

    def test_get(self, app):
        client = app.test_client()

        ingredient_info = dict()

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
            ['Black Beans','Black Bean Pineapple Salsa', 2, '15oz cans'],
            ['Pineapple','Black Bean Pineapple Salsa', 1, 'pineapple'],
            ['Tomato','Fruit Salad', 0.5, 'tomato'],
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

        # get recipes from ingredient
        response = client.get(f"ingredients/{ingredient_info['Tomato'][0]}/recipes")

        assert response.status_code == 200
        assert len(response.json) == 2

        # get recipes from ingredient with no recipes
        response = client.get(f"ingredients/{ingredient_info['Not Used'][0]}/recipes")

        assert response.status_code == 200
        assert len(response.json) == 0

        # get ingredients from recipe
        response = client.get(f"recipes/{recipe_ids['Black Bean Pineapple Salsa']}/ingredients")

        assert response.status_code == 200
        assert len(response.json) == 3

        # get ingredients from recipe with no ingredients
        response = client.get(f"recipes/{recipe_ids['Cauliflower Taco']}/ingredients")

        assert response.status_code == 200
        assert len(response.json) == 0

    def test_link(self, app):
        client = app.test_client()

        ingredient_info = dict()

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

        # link from recipes/id/ingredients
        associations = [
            ['Black Beans','Black Bean Pineapple Salsa', 2, '15oz cans'],
            ['Pineapple','Black Bean Pineapple Salsa', 1, 'pineapple'],
            ['Tomato','Fruit Salad', 0.5, 'tomato'],
        ]

        for i_name, r_name, amount, unit in associations:
            r_id = recipe_ids[r_name]
            i_id, _ = ingredient_info[i_name]

            response = client.post(f'/recipes/{r_id}/ingredients',
                headers = {"Content-Type":"application/json"},
                json = {'recipeIngredients': [{'ingredientId': i_id, 'amount': amount, 'unit': unit}]}
            )

            assert response.status_code == 204

        # link from ingredients/id/recipes
        associations = [
            ['Chicken Breast','Chicken Salad', 2, 'lbs'],
            ['Rice','Red Beans and Rice', 2, 'cups'],
            ['Tomato','Black Bean Pineapple Salsa', 2, 'tomato'],
        ]

        for i_name, r_name, amount, unit in associations:
            r_id = recipe_ids[r_name]
            i_id, _ = ingredient_info[i_name]

            response = client.post(f'/ingredients/{i_id}/recipes',
                headers = {"Content-Type":"application/json"},
                json = {'recipeIngredients': [{'recipeId': r_id, 'amount': amount, 'unit': unit}]}
            )

            assert response.status_code == 204

    def test_unlink(self, app):
        client = app.test_client()

        ingredient_info = dict()

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

        for ingredient in ingredients:
            response = client.post('/ingredients/', 
                headers = {"Content-Type":"application/json"},
                json = {'name':ingredient['name']}
            )

            assert response.status_code == 201

            ingredient_info[ingredient['name']] = (response.json['id'], response.headers['ETag'])

        recipe_info = dict()

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

            recipe_info[response.json['name']] = (response.json['id'], response.headers['ETag'])

        associations = [
            ['Black Beans','Black Bean Pineapple Salsa', 2, '15oz cans'],
            ['Pineapple','Black Bean Pineapple Salsa', 1, 'pineapple'],
            ['Tomato','Fruit Salad', 0.5, 'tomato'],
            ['Chicken Breast','Chicken Salad', 2, 'lbs'],
            ['Rice','Red Beans and Rice', 2, 'cups'],
            ['Tomato','Black Bean Pineapple Salsa', 2, 'tomato'],
        ]

        for i_name, r_name, amount, unit in associations:
            r_id, _ = recipe_info[r_name]
            i_id, _ = ingredient_info[i_name]

            response = client.post(f'/recipes/{r_id}/ingredients',
                headers = {"Content-Type":"application/json"},
                json = {'recipeIngredients': [{'ingredientId': i_id, 'amount': amount, 'unit': unit}]}
            )

            assert response.status_code == 204

        # delete recipe from ingredient/id/recipes
        response = client.delete(
            f"ingredients/{ingredient_info['Tomato'][0]}/recipes/{recipe_info['Black Bean Pineapple Salsa'][0]}",
            headers = {'If-Match': ingredient_info['Tomato'][1]}
        )

        assert response.status_code == 204

        # verify only one entry was deleted
        response = client.get(f"ingredients/{ingredient_info['Tomato'][0]}/recipes")

        assert response.status_code == 200
        print(ingredient_info['Tomato'][0],recipe_info['Black Bean Pineapple Salsa'][0])
        print(response.json)
        assert len(response.json) == 1

        # delete non-existant recipe from ingredient/id/recipes
        response = client.delete(
            f"ingredients/{ingredient_info['Not Used'][0]}/recipes/{recipe_info['Black Bean Pineapple Salsa'][0]}",
            headers = {'If-Match': ingredient_info['Not Used'][1]},
        )

        assert response.status_code == 422

        # delete ingredient from recipes/id/ingredient
        response = client.delete(
            f"recipes/{recipe_info['Black Bean Pineapple Salsa'][0]}/ingredients/{ingredient_info['Black Beans'][0]}",
            headers = {'If-Match': recipe_info['Black Bean Pineapple Salsa'][1]},
        )

        assert response.status_code == 204

        # verify only one entry was deleted
        response = client.get(f"recipes/{recipe_info['Black Bean Pineapple Salsa'][0]}/ingredients")

        assert response.status_code == 200
        assert len(response.json) == 1
