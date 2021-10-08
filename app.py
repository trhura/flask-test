from datetime import timedelta, datetime
import os
import uuid
import jwt

from flask import Flask, request, make_response, jsonify, make_response
from jsonschema import ValidationError
from flask_expects_json import expects_json

from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

app = Flask(__name__)
db.init_app(app)

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/test.db"


@app.route("/user", methods=["GET"])
def get_all_users():
    users = User.query.with_entities(
        User.public_id,
        User.name,
        User.admin,
    ).all()

    return jsonify({"users": [dict(user) for user in users]})


@app.route("/user", methods=["POST"])
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

    return jsonify({"message": "new user created"})


@app.route("/user/<public_id>", methods=["GET"])
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
        raise NotFound("no such user found")

    return jsonify({"user": dict(user)})


@app.route("/user/<public_id>", methods=["DELETE"])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        raise NotFound("no such user found")

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "the user has been deleted"})


@app.route(
    "/login",
)
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("could not verify", 401)

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response("could not verify", 401)

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {"sub": user.public_id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            app.config["SECRET_KEY"],
        )

        return jsonify({"auth_token": token})

    return make_response("could not verify", 401)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""

    message = e.description

    # use concise message for ValidationErrors
    if isinstance(e.description, ValidationError):
        message = e.description.message

    return make_response(
        jsonify(
            {
                "success": False,
                "message": message,
            }
        ),
        e.code,
    )


if __name__ == "__main__":
    app.run(debug=True)
