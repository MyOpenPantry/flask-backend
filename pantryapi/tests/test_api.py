import pytest, json
from datetime import datetime
from ..common.httpstatuscodes import HttpStatusCodes

def test_get_inventory(client):
    # TODO /v1 is defined as the prefix when initiating the API in create_app(). Is there a way to automatically get that definition here?
    response = client.get('/v1/inventory/')
    assert response.status_code == HttpStatusCodes.OK.value
    assert response.json == []

@pytest.mark.parametrize(
    "input_json, expected_json, expected_http_code",
    [
        pytest.param(
            json.dumps({'name':'Kroger Eggs', 'amount':12, 'product_id':123456,}),
            {'item':{'id':1,'name':'Kroger Eggs', 'amount':12, 'product_id':123456,'ingredient_id':None,'updated':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}},
            HttpStatusCodes.OK.value
        ),
        pytest.param(
            json.dumps({'amount':12, 'product_id':123456,}),
            {'message': {'name': 'No name was provided for the item'}},
            HttpStatusCodes.BAD_REQUEST.value
        ),
    ],
)
def test_post_inventory(client, input_json, expected_json, expected_http_code):
    response = client.post('/v1/inventory/', 
        headers = {"Content-Type": "application/json"},
        data = input_json
    )
    assert response.status_code == expected_http_code

    print()
    for k in response.json:
        for k2 in response.json[k]:
            # updated can differ depending on the speed of the test, so ignore it for now
            if k2 == 'updated':
                continue
            assert response.json[k][k2] == expected_json[k][k2]

