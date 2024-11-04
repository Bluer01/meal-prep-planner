import pytest
from app import create_app
from app.database import init_db, get_db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:'
    })
    
    with app.app_context():
        init_db()
    
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Meal Prep Planner' in response.data

def test_add_recipe(client):
    recipe_data = {
        'name': 'Test Recipe',
        'servings': 4,
        'ingredients': [
            {'name': 'test ingredient', 'amount': 100, 'unit': 'g'}
        ]
    }
    response = client.post('/recipes', json=recipe_data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_get_recipes(client):
    response = client.get('/recipes')
    assert response.status_code == 200
    assert isinstance(response.json, list)