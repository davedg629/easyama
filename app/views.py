from app import app, db, r
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup, g
from app.forms import ThreadForm
from app.models import Thread, User
from flask.ext.login import login_user, logout_user, \
    login_required, current_user
from app.utils import generate_token
import praw


@app.before_request
def before_request():
    if current_user.is_authenticated():
        g.user = current_user
    else:
        g.user = None


# REDDIT LOGIN
@app.route('/authorize/')
def authorize():
    state = request.args.get('state', '')
    if current_user.is_anonymous() and (state == session['oauth_token']):
        try:
            code = request.args.get('code', '')
            access_info = r.get_access_information(code)
            user_reddit = r.get_me()
            user = db.session.query(User)\
                .filter_by(username=user_reddit.name)\
                .first()
            if user is None:
                user = User(
                    username=user_reddit.name,
                    role_id=2,
                    refresh_token=access_info['refresh_token']
                )
                db.session.add(user)
                db.session.commit()
            else:
                user.refresh_token = access_info['refresh_token']
                db.session.commit()
            login_user(user)
            flash('Hi ' + user.username + '! You have successfully' +
                  ' logged in with your reddit account.')
            return redirect(url_for('index'))
        except praw.errors.OAuthException:
            flash('There was a problem with your login. Please try again.')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


# logout
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated():
        form = ThreadForm()
        if form.validate_on_submit():

            new_thread = Thread(
                user_id=1,
                title=form.title.data,
                body=form.body.data,
                verification=form.verification.data,
                subreddit=form.subreddit.data,
            )
            db.session.add(new_thread)
            db.session.commit()

            return redirect(url_for(
                'preview',
                thread_id=new_thread.id
            ))

        return render_template(
            'index.html',
            page_title="Start Your reddit AMA",
            form=form
        )
    else:
        session['oauth_token'] = generate_token()
        oauth_link = r.get_authorize_url(
            session['oauth_token'],
            ['identity', 'submit'],
            True
        )
        return render_template(
            'index-anon.html',
            page_title="Start Your reddit AMA",
            oauth_link=oauth_link
        )


@app.route("/preview/<int:thread_id>")
def preview(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread:
        return render_template(
            'preview.html',
            thread=thread
        )
    else:
        abort(404)


@app.route("/success")
def success():
    return 'Success!'
