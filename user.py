import jwt
import uuid

from datetime import timedelta, datetime
from flask import Blueprint, request, current_app
from sqlalchemy import exc

from flask_expects_json import expects_json
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from decorators import auth_token_optional, auth_token_required
from response import (
    AuthorizationError,
    ExistingUserError,
    UserNotFound,
    AuthenticationFailure,
    DatabaseError,
    success_json,
)

api = Blueprint("users", __name__)


@api.route("/users", methods=["GET"])
@auth_token_required
def list_users():
    if not request.admin_user:
        raise AuthorizationError("only admin user can access this route")

    pagination = User.query.with_entities(
        User.uuid,
        User.username,
        User.fullname,
        User.admin,
    ).paginate(max_per_page=30)

    return success_json(
        current_page=pagination.page,
        prev_page=pagination.prev_num,
        next_page=pagination.next_num,
        per_page=pagination.per_page,
        pages=pagination.pages,
        total=pagination.total,
        users=[dict(user) for user in pagination.items],
    )


@api.route("/users", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {
            "fullname": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "admin": {"type": "boolean"},
        },
        "required": ["fullname", "password", "username"],
    }
)
@auth_token_optional
def create_user():
    data = request.get_json()
    admin = False

    if "admin" in data:
        if not hasattr(request, "admin_user") or not request.admin_user:
            raise AuthorizationError("only admin can create admin users")
        else:
            admin = True

    hashed_password = generate_password_hash(data["password"], method="sha256")
    new_user = User(
        uuid=str(uuid.uuid4()),
        fullname=data["fullname"],
        username=data["username"],
        password=hashed_password,
        admin=admin,
    )

    try:
        db.session.add(new_user)
        db.session.commit()

    except exc.IntegrityError:
        db.session.rollback()
        raise ExistingUserError()

    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        db.session.rollback()
        raise DatabaseError()

    return success_json(message="new user created")


@api.route("/users/<uuid>", methods=["GET"])
@auth_token_required
def get_user(uuid):
    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError("you are not allowed to access other users")

    user = (
        User.query.filter_by(uuid=uuid)
        .with_entities(
            User.uuid,
            User.fullname,
            User.username,
            User.admin,
        )
        .first()
    )

    if not user:
        raise UserNotFound()

    return success_json(user=dict(user))


@api.route("/users/<uuid>", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {
            "fullname": {"type": "string"},
            "password": {"type": "string"},
            "admin": {"type": "boolean"},
        },
        "anyOf": [
            {"required": ["fullname"]},
            {"required": ["password"]},
            {"required": ["admin"]},
        ],
    }
)
@auth_token_required
def update_user(uuid):
    data = request.get_json()

    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError("you are not allowed to update other users")

    try:
        user = User.query.filter_by(uuid=uuid).first()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        raise DatabaseError()

    if not user:
        raise UserNotFound()

    if "fullname" in data:
        user.fullname = data["fullname"]

    if "password" in data:
        user.password = generate_password_hash(data["password"], method="sha256")

    if "admin" in data:
        if not request.admin_user:
            raise AuthorizationError("only admin can update admin users")

        user.admin = data["admin"]

    try:
        db.session.commit()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        db.session.rollback()
        raise DatabaseError()

    return success_json(message="user updated successfully")


@api.route("/users/<uuid>", methods=["DELETE"])
@auth_token_required
def delete_user(uuid):
    if not request.admin_user:
        raise AuthorizationError("only admin user can access this route")

    user = User.query.filter_by(uuid=uuid).first()

    if not user:
        raise UserNotFound()

    db.session.delete(user)
    db.session.commit()

    return success_json(message="the user has been deleted")


@api.route("/login", methods=["POST"])
def user_login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        raise AuthenticationFailure()

    user = (
        User.query.with_entities(
            User.uuid,
            User.username,
            User.fullname,
            User.admin,
            User.password,
        )
        .filter_by(username=auth.username)
        .first()
    )
    if not user:
        raise AuthenticationFailure()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "sub": user.uuid,
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "adm": user.admin,
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        user_dict = user = dict(user)
        del user_dict["password"]

        return success_json(auth_token=token, user=user_dict)

    raise AuthenticationFailure()
