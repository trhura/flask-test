import os
import pytest

from app import app
from models import db

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/test.db"
app.config["TESTING"] = True

db.init_app(app)


@pytest.fixture(scope="module")
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
