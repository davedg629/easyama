from app import app, db, models
from flask import abort
from flask.ext.login import current_user
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView


class AuthMixin(object):
    def is_accessible(self):
        if current_user.is_authenticated():
            if current_user.role_id is 1:
                return True
            else:
                return False
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return abort(404)


class MyAdminIndexView(AuthMixin, AdminIndexView):
    pass


class AdminModelView(AuthMixin, ModelView):
    pass

admin = Admin(
    name='EasyAMA',
    index_view=MyAdminIndexView()
)
