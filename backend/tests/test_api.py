import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.database import engine
from backend.app.main import app
import asyncio


# Синхронный тестовый клиент
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# Асинхронная очистка базы через отдельный event loop
@pytest.fixture(autouse=True)
def cleanup_db():
    async def async_cleanup():
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM tasks"))
            await conn.execute(text("DELETE FROM users"))
            await conn.commit()

    # Запуск асинхронной функции в синхронном контексте
    asyncio.run(async_cleanup())


@pytest.fixture
def test_user(client):
    user_data = {
        "username": "test@example.com",
        "password": "strongpassword"
    }
    client.post("/api/auth/register", data=user_data)
    return user_data


@pytest.fixture
def auth_headers(client, test_user):
    login_response = client.post("/api/auth/login", data=test_user)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_task(client, auth_headers):
    task_data = {"title": "Test Task", "description": "Test Description"}
    response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
    return response.json()["id"]


def test_user_registration(client):
    # Тест регистрации пользователя
    user_data = {
        "username": "new@user.com",
        "password": "newpassword"
    }
    response = client.post("/api/auth/register", data=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_duplicate_registration(client, test_user):
    # Тест регистрации с существующим email
    response = client.post("/api/auth/register", data=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_with_invalid_credentials(client):
    # Тест входа с неверными данными
    response = client.post("/api/auth/login", data={
        "username": "wrong@email.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_login_success(client, test_user):
    # Тест успешного входа
    response = client.post("/api/auth/login", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_task(client, auth_headers):
    # Тест создания задачи
    task_data = {
        "title": "New Task",
        "description": "Task Description"
    }
    response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == task_data["title"]


def test_get_tasks_empty(client, auth_headers):
    # Тест получения пустого списка задач
    response = client.get("/api/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_tasks_with_items(client, auth_headers, test_task):
    # Тест получения списка задач
    response = client.get("/api/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_task(client, auth_headers, test_task):
    # Тест обновления задачи
    update_data = {"title": "Updated Task", "is_completed": True}
    response = client.put(
        f"/api/tasks/{test_task}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["is_completed"] is True


def test_delete_task(client, auth_headers, test_task):
    # Тест удаления задачи
    response = client.delete(
        f"/api/tasks/{test_task}",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Проверка что задача удалена
    check_response = client.get("/api/tasks/", headers=auth_headers)
    assert len(check_response.json()) == 0


def test_protected_routes(client):
    # Тест защиты эндпоинтов
    routes = [
        ("GET", "/api/tasks/"),
        ("POST", "/api/tasks/"),
        ("PUT", "/api/tasks/1"),
        ("DELETE", "/api/tasks/1")
    ]

    for method, url in routes:
        if method == "GET":
            response = client.get(url)
        elif method == "POST":
            response = client.post(url)
        elif method == "PUT":
            response = client.put(url)
        elif method == "DELETE":
            response = client.delete(url)

        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers