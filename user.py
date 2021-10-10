import jwt
import uuid

from datetime import timedelta, datetime
from flask import Blueprint, request, current_app

from flask_expects_json import expects_json
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from decorators import auth_token_optional, auth_token_required
from response import (
    AuthorizationError,
    success_json,
    UserNotFound,
    AuthenticationFailure,
)

api = Blueprint("users", __name__)


@api.route("/user", methods=["GET"])
@auth_token_required
def get_all_users():
    if not request.admin_user:
        raise AuthorizationError("only admin user can access this route")

    users = User.query.with_entities(
        User.public_id,
        User.name,
        User.admin,
    ).all()

    return success_json(users=[dict(user) for user in users])


@api.route("/user", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "password": {"type": "string"},
            "admin": {"type": "boolean"},
        },
        "required": ["name", "password"],
    }
)
@auth_token_optional
def create_user():
    data = request.get_json()
    admin = False

    if "admin" in data:
        if not request.admin_user:
            raise AuthorizationError("only admin can create admin users")
        else:
            admin = True

    hashed_password = generate_password_hash(data["password"], method="sha256")
    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data["name"],
        password=hashed_password,
        admin=admin,
    )

    db.session.add(new_user)
    db.session.commit()

    return success_json(message="new user created")


@api.route("/user/<public_id>", methods=["GET"])
@auth_token_required
def get_one_user(public_id):
    if not request.admin and request.user_id != public_id:
        raise AuthorizationError("you are not allowed to access other users")

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


@api.route("/user/<public_id>", methods=["DELETE"])
@auth_token_required
def delete_user(public_id):
    if not request.admin_user:
        raise AuthorizationError("only admin user can access this route")

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        raise UserNotFound()

    db.session.delete(user)
    db.session.commit()

    return success_json(message="the user has been deleted")


@api.route("/login")
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        raise AuthenticationFailure()

    user = User.query.filter_by(name=auth.username).first()
    if not user:
        raise AuthenticationFailure()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "sub": user.public_id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "adm": user.admin,
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        return success_json(auth_token=token)

    raise AuthenticationFailure()