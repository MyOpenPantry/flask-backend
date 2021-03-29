import pytest

from myopenpantry import create_app

@pytest.fixture
def app():
    application = create_app(config_name='testing')
    application.config['TESTING'] = True
    return application