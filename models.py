from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean)


class Timzeone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64))
    name = db.Column(db.String(32))
    city_name = db.Column(db.String(32))
    difference = db.Column(db.Integer)
