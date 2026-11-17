import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.security as security
from src.customer_api import app
from src.database import get_db
from src.models import Base


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
