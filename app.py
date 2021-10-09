import os

from flask import Flask
from werkzeug.exceptions import HTTPException

from models import db
from users import user_api
from response import handle_http_exception


app = Flask(__name__)
db.init_app(app)

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/test.db"

app.register_blueprint(user_api)
app.register_error_handler(HTTPException, handle_http_exception)


if __name__ == "__main__":
    app.run(debug=True)
