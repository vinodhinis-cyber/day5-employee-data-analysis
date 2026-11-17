import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.security as security
from src.customer_api import app
from src.database import get_db
from src.models import Base

API_HEADERS = {"X-API-Key": "test-api-key"}

CUSTOMER_DATA = {
    "name": "Divya",
    "email": "divya@example.com",
    "phone": "9876543210",
    "city": "Chennai",
}


@pytest.fixture
def client(tmp_path, monkeypatch):

    database_file = tmp_path / "test.db"

    engine = create_engine(
        f"sqlite:///{database_file}", connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(security, "SECRET_API_KEY", "test-api-key")

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_customer(client):
    response = client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    assert response.status_code == 201
    assert response.json()["name"] == "Divya"


def test_get_customers(client):
    client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    response = client.get("/customers", headers=API_HEADERS)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_customer_not_found(client):
    response = client.get("/customers/999", headers=API_HEADERS)
    assert response.status_code == 404


def test_duplicate_email(client):
    client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    response = client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    assert response.status_code == 409


def test_invalid_email(client):
    invalid_data = {"name": "Test", "email": "not-an-email"}

    response = client.post("/customers", json=invalid_data, headers=API_HEADERS)

    assert response.status_code == 422


def test_missing_api_key(client):
    response = client.get("/customers")
    assert response.status_code == 401


def test_invalid_api_key(client):
    response = client.get("/customers", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403


def test_update_customer(client):
    create_response = client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}", json={"city": "Bangalore"}, headers=API_HEADERS
    )

    assert response.status_code == 200
    assert response.json()["city"] == "Bangalore"


def test_update_customer_not_found(client):
    response = client.put(
        "/customers/999", json={"city": "Bangalore"}, headers=API_HEADERS
    )

    assert response.status_code == 404


def test_delete_customer(client):
    create_response = client.post("/customers", json=CUSTOMER_DATA, headers=API_HEADERS)

    customer_id = create_response.json()["id"]

    response = client.delete(f"/customers/{customer_id}", headers=API_HEADERS)

    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"


def test_delete_customer_not_found(client):
    response = client.delete("/customers/999", headers=API_HEADERS)

    assert response.status_code == 404


def test_customer_pagination(client):
    for number in range(3):
        data = {"name": f"Customer {number}", "email": f"customer{number}@example.com"}
        client.post("/customers", json=data, headers=API_HEADERS)

    response = client.get("/customers?page=1&per_page=2", headers=API_HEADERS)

    assert response.status_code == 200
    assert len(response.json()) == 2
