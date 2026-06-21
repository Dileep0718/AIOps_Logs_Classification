"""

conftest.py

-----------

Shared test configuration.

Mocks heavy ML models so CI does not need to download them.

Uses SQLite for tests instead of PostgreSQL.

"""
 
import sys

import pytest

from unittest.mock import MagicMock

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
 
# mock heavy ML libraries BEFORE any app imports

# this prevents sentence-transformers from downloading models during CI

sys.modules["sentence_transformers"] = MagicMock()
 
import joblib

joblib.load = MagicMock(return_value={

    "model"  : MagicMock(

        predict_proba = MagicMock(return_value=[[0.1, 0.8, 0.1]]),

        classes_      = ["Error", "HTTP Status", "System Notification"]

    ),

    "encoder": MagicMock(

        encode = MagicMock(return_value=[[0.1, 0.2, 0.3]])

    )

})
 
# now safe to import app

from app.main import app

from app.models.database import Base, get_db
 
# SQLite test database

TEST_DATABASE_URL = "sqlite:///./test.db"
 
engine = create_engine(

    TEST_DATABASE_URL,

    connect_args={"check_same_thread": False}

)
 
TestingSessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)
 
 
def override_get_db():

    db = TestingSessionLocal()

    try:

        yield db

    finally:

        db.close()
 
 
app.dependency_overrides[get_db] = override_get_db
 
 
@pytest.fixture(autouse=True)

def setup_test_db():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
 