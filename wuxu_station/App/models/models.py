from App.exts import db
from datetime import datetime


# 用户
class UserModel(db.Model):
    __tablename__ = "tb_user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nicheng = db.Column(db.String(6), default="")
    schools = db.Column(db.String(10))
    sex = db.Column(db.Integer)
    brief = db.Column(db.Text(), default="")
    img = db.Column(db.String(100))


class Advice(db.Model):
    __tablename__ = "advice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text())
    telephone = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))


class Score(db.Model):
    __tablename__ = "test_score"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feeling = db.Column(db.Integer, default=0)
    anxiety = db.Column(db.Integer, default=0)
    depress = db.Column(db.Integer, default=0)
    character = db.Column(db.Integer, default=0)
    user_name = db.Column(db.String(20))


class Forum(db.Model):
    __tablename__ = "forum"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text(), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    img = db.Column(db.String(100))
    url = db.Column(db.String(100))
    likes=db.Column(db.Integer,default=0)

    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))
    user = db.relationship("UserModel", backref="forums")

class Answer(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text(), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    img = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey(Forum.id))
    speaker_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))

    author = db.relationship(
        "Forum", backref=db.backref("answers", order_by=create_time.desc())
    )
    speaker = db.relationship("UserModel", backref="answers")


class Collect(db.Model):
    __tablename__ = "collect"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text(), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_create = db.Column(db.DateTime)
    img = db.Column(db.String(100))
    url = db.Column(db.String(100))

    author_id = db.Column(db.Integer, db.ForeignKey(Forum.id))
    author = db.relationship(
        "Forum", backref=db.backref("collect", order_by=create_time.desc())
    )
    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))
    user = db.relationship("UserModel", backref="collect")
