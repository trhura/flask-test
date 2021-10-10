from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

from datetime import timedelta


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(64))
    admin = db.Column(db.Boolean)


class Timezone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), ForeignKey(User.uuid))
    name = db.Column(db.String(32))
    tzname = db.Column(db.String(32))
    utcoffset = db.Column(db.Integer)

    def asdict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "tzname": self.tzname,
            "utcoffset": str(timedelta(seconds=self.utcoffset)),
        }
