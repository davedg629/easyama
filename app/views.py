from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup, g
from app.forms import ThreadForm
from app.models import Thread
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
@app.route('/login/')
def login():
    if current_user.is_anonymous():
        session['oauth_token'] = generate_token()
        oauth_link = r.get_authorize_url(
            session['oauth_token'],
            ['identity', 'submit', 'edit'],
            True
        )
        return render_template(
            'login.html',
            title="Reddit Login",
            page_title="Reddit Login",
            oauth_link=oauth_link
        )
    else:
        flash('You are already logged in!')
        return redirect(url_for('dashboard'))


@app.route("/", methods=['GET', 'POST'])
def index():
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
