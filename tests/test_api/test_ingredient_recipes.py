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
                json = {'recipe_ingredients': [{'ingredient_id': i_id, 'amount':amount, 'unit':unit}]}
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
        pass

    def test_unlink(self, app):
        pass
