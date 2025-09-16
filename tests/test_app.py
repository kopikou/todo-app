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
    assert response.status_code == 302 

def test_get_todos_api(client):
    response = client.get('/api/todos')
    assert response.status_code == 200
    assert response.is_json

def test_delete_todo(client):
    # Очищаем список перед тестом
    from app import todos
    todos.clear()

    client.post('/add', data={'todo': 'Task to delete'})

    response = client.get('/api/todos')
    tasks_before = response.get_json()

    last_task_id = tasks_before[-1]['id'] if tasks_before else None
    response = client.get(f'/delete/{last_task_id}')

    response = client.get('/api/todos')
    tasks_after = response.get_json()
    
    assert len(tasks_after) == 0