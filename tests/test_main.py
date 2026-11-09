import json

import pytest
from fastapi.testclient import TestClient

from src import main

client = TestClient(main.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_employees():
    response = client.get("/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_employee_success():
    response = client.get("/employees/Divya")
    assert response.status_code == 200
    assert response.json()["name"] == "Divya"


def test_get_employee_not_found():
    response = client.get("/employees/Unknown")
    assert response.status_code == 404


@pytest.fixture
def test_data_file(tmp_path, monkeypatch):
    file_path = tmp_path / "employees.json"

    file_path.write_text(
        json.dumps([{"name": "Ravi", "salary": 50000}]), encoding="utf-8"
    )

    monkeypatch.setattr(main, "DATA_FILE", file_path)
    return file_path


def test_create_employee(test_data_file):
    response = client.post("/employees", json={"name": "Kavya", "salary": 45000})

    assert response.status_code == 201
    assert response.json() == {"name": "Kavya", "salary": 45000}


def test_invalid_salary():
    response = client.post("/employees", json={"name": "Test", "salary": -5})
    assert response.status_code == 422


def test_empty_name():
    response = client.post("/employees", json={"name": "", "salary": 45000})

    assert response.status_code == 422
