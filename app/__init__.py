from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from flask.ext.markdown import Markdown

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
bootstrap = Bootstrap(app)
manager = Manager(app)
pagedown = PageDown(app)
md = Markdown(app)

from app import models, views, admin_views
from admin_views import admin
admin.init_app(app)
