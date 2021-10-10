import os

from pytz import timezone
from datetime import datetime
from flask import Flask, request
from werkzeug.exceptions import HTTPException

from models import db, Timezone
from decorators import auth_token_required
from response import success_json

import user
import timezones

from response import http_exception_handler


app = Flask(__name__, static_folder=None)

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(user.api)
app.register_blueprint(timezones.api)
app.register_error_handler(HTTPException, http_exception_handler)


@app.route("/time", methods=["GET"])
@auth_token_required
def get_time():
    times = {}
    timezones = Timezone.query.filter_by(user_id=request.user_id).all()

    for tz in timezones:
        times[tz.name] = datetime.now(timezone(tz.tzname)).strftime("%Y-%m-%d %H:%M:%S")

    return success_json(time=times)


if __name__ == "__main__":
    app.run(debug=True)
