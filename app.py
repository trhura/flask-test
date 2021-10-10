import os

from flask import Flask
from werkzeug.exceptions import HTTPException

from models import db
from user import api
from response import http_exception_handler


app = Flask(__name__, static_folder=None)

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(api)
app.register_error_handler(HTTPException, http_exception_handler)


if __name__ == "__main__":
    app.run(debug=True)
