import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'To-Do List' in response.data

def test_add_todo(client):
    response = client.post('/add', data={'todo': 'Test task'})
    assert response.status_code == 302  # Redirect

def test_get_todos_api(client):
    response = client.get('/api/todos')
    assert response.status_code == 200
    assert response.is_json