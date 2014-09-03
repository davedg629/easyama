from app import db
from datetime import datetime
from app.utils import make_slug


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


class User(db.Model):

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

    def get_slug(context):
        return make_slug(context.current_parameters['title'])

    slug = db.Column(
        db.String,
        nullable=False,
        default=get_slug
    )

    reddit_id = db.Column(db.String)
    reddit_permalink = db.Column(db.String)
    subreddit = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False, default=1)
    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
        nullable=False
    )

    def __unicode__(self):
        return self.title + ' - ' + str(self.category_id)
