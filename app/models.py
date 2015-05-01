from app import db, login_manager
from datetime import datetime
from flask.ext.login import UserMixin


class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    users = db.relationship(
        'User',
        backref='role',
        lazy='dynamic'
    )

    def __unicode__(self):
        return self.name


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    refresh_token = db.Column(db.String)

    threads = db.relationship(
        'Thread',
        backref='user',
        lazy='dynamic'
    )

    def __unicode__(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Thread(db.Model):

    __tablename__ = "threads"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    verification = db.Column(db.String, nullable=False)
    subreddit = db.Column(db.String, nullable=False)

    submitted = db.Column(db.Boolean, nullable=False, default=False)

    reddit_id = db.Column(db.String)
    reddit_permalink = db.Column(db.String)
    score = db.Column(db.Integer, nullable=False, default=1)

    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
        nullable=False
    )

    def __unicode__(self):
        return self.title + ' - ' + str(self.id)
