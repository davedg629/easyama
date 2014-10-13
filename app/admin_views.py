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


class RoleView(AdminModelView):
    pass


class UserView(AdminModelView):
    pass


class ThreadView(AdminModelView):
    form_excluded_columns = ('score')


# Admin constructor
admin = Admin(
    name='EasyAMA',
    index_view=MyAdminIndexView()
)

# add admin views
admin.add_view(RoleView(
    models.Role,
    db.session,
    name='Roles',
    endpoint='role_model_view'
))
admin.add_view(UserView(
    models.User,
    db.session,
    name='Users',
    endpoint='user_model_view'
))
admin.add_view(ThreadView(
    models.Thread,
    db.session,
    name='Threads',
    endpoint='thread_model_view'
))
