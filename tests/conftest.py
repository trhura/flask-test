import os
import jwt
import uuid
import pytest

from pytz import timezone
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import app
from models import db, User, Timezone

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


@pytest.fixture
def randname():
    """to generate random username fixture"""
    yield str(uuid.uuid4())


@pytest.fixture
def usera():
    user = User(
        uuid=str(uuid.uuid4()),
        fullname="User A",
        username="usera",
        password=generate_password_hash("passa", method="sha256"),
        admin=False,
    )

    db.session.add(user)
    db.session.commit()

    yield user

    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def userb():
    user = User(
        uuid=str(uuid.uuid4()),
        fullname="User B",
        username="userb",
        password=generate_password_hash("passb", method="sha256"),
        admin=False,
    )

    db.session.add(user)
    db.session.commit()

    yield user

    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def adminuser():
    user = User(
        uuid=str(uuid.uuid4()),
        fullname="Admin User",
        username="adminuser",
        password=generate_password_hash("adminpass", method="sha256"),
        admin=True,
    )

    db.session.add(user)
    db.session.commit()

    yield user

    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def usera_auth_token(usera):
    return jwt.encode(
        {
            "sub": usera.uuid,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "adm": False,
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )


@pytest.fixture
def userb_auth_token(userb):
    return jwt.encode(
        {
            "sub": userb.uuid,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "adm": False,
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )


@pytest.fixture
def admin_auth_token(adminuser):
    return jwt.encode(
        {
            "sub": adminuser.uuid,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "adm": True,
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )


@pytest.fixture
def tza1(usera):
    tza = Timezone(
        user_id=usera.uuid,
        name="Yangon City",
        tzname="Asia/Yangon",
        utcoffset=timezone("Asia/Yangon")._utcoffset.total_seconds(),
    )

    db.session.add(tza)
    db.session.commit()

    yield tza

    db.session.delete(tza)
    db.session.commit()


@pytest.fixture
def tza2(usera):
    tza = Timezone(
        user_id=usera.uuid,
        name="Seoul City",
        tzname="Asia/Seoul",
        utcoffset=timezone("Asia/Seoul")._utcoffset.total_seconds(),
    )

    db.session.add(tza)
    db.session.commit()

    yield tza

    db.session.delete(tza)
    db.session.commit()


@pytest.fixture
def tzb1(userb):
    tzb = Timezone(
        user_id=userb.uuid,
        name="Singapore City",
        tzname="Asia/Singapore",
        utcoffset=timezone("Asia/Singapore")._utcoffset.total_seconds(),
    )

    db.session.add(tzb)
    db.session.commit()

    yield tzb

    db.session.delete(tzb)
    db.session.commit()
