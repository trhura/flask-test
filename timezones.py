from pytz import all_timezones, timezone
from flask import Blueprint, request, current_app

from sqlalchemy import exc
from flask_expects_json import expects_json

from models import Timezone, db
from decorators import auth_token_required
from response import (
    AuthorizationError,
    TimezoneNotFound,
    InvalidTimezoneError,
    DatabaseError,
    success_json,
)

api = Blueprint("timezones", __name__)


@api.route("/users/<uuid>/timezones", methods=["GET"])
@auth_token_required
def list_timezones(uuid):
    timezones = Timezone.query.filter_by(user_id=uuid).all()

    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError("you are not allowed to get timezone of other users")

    return success_json(timezones=[tz.asdict() for tz in timezones])


@api.route("/users/<uuid>/timezones", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "tzname": {"type": "string"},
        },
        "required": ["name", "tzname"],
    }
)
@auth_token_required
def create_timezone(uuid):
    data = request.get_json()

    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError(
            "you are not allowed to create timezone for other users"
        )

    if data["tzname"] not in all_timezones:
        raise InvalidTimezoneError()

    tzinfo = timezone(data["tzname"])
    tz = Timezone(
        user_id=uuid,
        name=data["name"],
        tzname=data["tzname"],
        utcoffset=tzinfo._utcoffset.total_seconds(),
    )

    try:
        db.session.add(tz)
        db.session.commit()

    except exc.SQLAlchemyError as ex:
        db.session.rollback()
        current_app.logger.error(ex)
        raise DatabaseError()

    return success_json(message="new timezone added")


@api.route("/users/<uuid>/timezones/<tzid>", methods=["GET"])
@auth_token_required
def get_timezone(uuid, tzid):
    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError("you are not allowed to get timezone of other users")

    try:
        timezone = Timezone.query.filter_by(user_id=uuid, id=tzid).first()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        raise DatabaseError()

    if not timezone:
        raise TimezoneNotFound()

    return success_json(timezone=timezone.asdict())


@api.route("/users/<uuid>/timezones/<tzid>", methods=["POST"])
@expects_json(
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "tzname": {"type": "string"},
        },
        "anyOf": [
            {"required": ["name"]},
            {"required": ["tzname"]},
        ],
    }
)
@auth_token_required
def update_timezone(uuid, tzid):
    data = request.get_json()

    try:
        tzrecord = Timezone.query.filter_by(user_id=uuid, id=tzid).first()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        raise DatabaseError()

    if not tzrecord:
        raise TimezoneNotFound()

    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError(
            "you are not allowed to update timezone for other users"
        )

    if "name" in data:
        tzrecord.name = data["name"]

    if "tzname" in data:
        if data["tzname"] not in all_timezones:
            raise InvalidTimezoneError()

        tzrecord.tzname = data["tzname"]
        tzrecord.utcoffset = timezone(tzrecord.tzname)._utcoffset.total_seconds()

    try:
        db.session.commit()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        db.session.rollback()
        raise DatabaseError()

    return success_json(message="timezone updated successfully")


@api.route("/users/<uuid>/timezones/<tzid>", methods=["DELETE"])
@auth_token_required
def delete_timezone(uuid, tzid):
    try:
        tzrecord = Timezone.query.filter_by(user_id=uuid, id=tzid).first()
    except exc.SQLAlchemyError as ex:
        current_app.logger.error(ex)
        raise DatabaseError()

    if not tzrecord:
        raise TimezoneNotFound()

    if not request.admin_user and request.user_id != uuid:
        raise AuthorizationError(
            "you are not allowed to delete timezone for other users"
        )

    db.session.delete(tzrecord)
    db.session.commit()

    return success_json(message="the timezone has been deleted")
