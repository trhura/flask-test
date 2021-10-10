from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


@dataclass
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(64))
    admin = db.Column(db.Boolean)


class Timzeone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))
    name = db.Column(db.String(32))
    city_name = db.Column(db.String(32))
    difference = db.Column(db.Integer)
