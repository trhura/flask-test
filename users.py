import jwt
import uuid

from datetime import timedelta, datetime
from flask import Blueprint, request, current_app

from flask_expects_json import expects_json
from werkzeug.security import generate_password_hash, check_password_hash

from response import UserNotFound, AuthenticationFailure, success_json
from models import db, User

user_api = Blueprint("users", __name__)


@user_api.route("/user", methods=["GET"])
def get_all_users():
    users = User.query.with_entities(
        User.public_id,
        User.name,
        User.admin,
    ).all()

    return success_json(users=[dict(user) for user in users])


@user_api.route("/user", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {"name": {"type": "string"}, "password": {"type": "string"}},
        "required": ["name", "password"],
    }
)
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data["password"], method="sha256")
    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data["name"],
        password=hashed_password,
        admin=False,
    )

    db.session.add(new_user)
    db.session.commit()

    return success_json(messsage="new user created")


@user_api.route("/user/<public_id>", methods=["GET"])
def get_one_user(public_id):
    user = (
        User.query.filter_by(public_id=public_id)
        .with_entities(
            User.public_id,
            User.name,
            User.admin,
        )
        .first()
    )

    if not user:
        raise UserNotFound()

    return success_json(user=dict(user))


@user_api.route("/user/<public_id>", methods=["DELETE"])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        raise UserNotFound()

    db.session.delete(user)
    db.session.commit()

    return success_json(message="the user has been deleted")


@user_api.route(
    "/login",
)
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        raise AuthenticationFailure()

    user = User.query.filter_by(name=auth.username).first()
    if not user:
        raise AuthenticationFailure()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {"sub": user.public_id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            current_app.config["SECRET_KEY"],
        )

        return success_json(auth_token=token)

    raise AuthenticationFailure()
