import pytest, json
from datetime import datetime
import dateutil.parser

class TestTags:
    def test_get_empty(self, app):
        client = app.test_client()

        response = client.get('/tags/')
        assert response.status_code == 200
        assert len(response.json) == 0

    def test_get_nonempty(self, app):
        client = app.test_client()

        tag = {
            'name':'greek',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        response = client.get('/tags/')
        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_item(self, app):
        client = app.test_client()

        tag = {
            'name':'chicken',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        id = response.json['id']

        response = client.get(f'/tags/{id}')

        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == tag['name']

    def test_get_invalid(self, app):
        client = app.test_client()

        tag = {
            'name':'beef',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
             json = tag,
        )

        id = response.json['id']

        response = client.get(f'/tags/{id+1}')

        assert response.status_code == 404

    def test_post(self, app):
        client = app.test_client()

        tag = {
            'name':'chicken',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

    def test_post_invalid(self, app):
        client = app.test_client()

        tag = {}

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 422

    def test_post_existing(self, app):
        client = app.test_client()

        tag = {
            'name':'chicken',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
           json = tag,
        )

        id = response.json['id']

        response = client.get(f'/tags/{id}')

        assert response.status_code == 200

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 422

    def test_put(self, app):
        client = app.test_client()

        tag = {
            'name':'vegetaria',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        tag['name'] = 'vegetarian'

        response = client.put(f'/tags/{id}', 
            headers = {"If-Match": etag},
            json = tag,
        )

        assert response.status_code == 200
        assert response.json['name'] == tag['name']

    def test_invalid_put(self, app):
        client = app.test_client()

        tag = {
            'name':'vegetaria',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        del tag['name']

        response = client.put(f'/tags/{id}', 
            headers = {"If-Match": etag},
            json = tag,
        )

        assert response.status_code == 422

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

    def test_delete(self, app):
        client = app.test_client()

        tag = {
            'name':'vegetaria',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 201
        assert response.json['name'] == tag['name']

        etag = response.headers['ETag']
        id = response.json['id']

        response = client.delete(f'/tags/{id}', 
            headers = {"If-Match": etag},
        )

        assert response.status_code == 204

    def test_delete_invalid(self, app):
        client = app.test_client()

        tag = {
            'name':'savory',
        }

        response = client.post('/tags/', 
            headers = {"Content-Type": "application/json"},
            json = tag,
        )

        assert response.status_code == 201

        etag = response.headers['ETag']
        id = response.json['id']

        response = client.delete(f'/tags/{id}', 
            headers = {"If-Match": etag},
        )

        assert response.status_code == 204

        response = client.delete(f'/tags/{id}', 
            headers = {"If-Match": etag},
        )

        assert response.status_code == 404
