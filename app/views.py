from app import app, db, r
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, g
from app.forms import ThreadForm
from app.models import Thread, User
from flask.ext.login import login_user, logout_user, \
    login_required, current_user
from app.utils import generate_token, reddit_body
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
                user_id=g.user.id,
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
            page_title="Step 2: Create your reddit AMA",
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
            page_title="Step 1: Login to your reddit account",
            oauth_link=oauth_link
        )


@app.route("/preview/<int:thread_id>")
@login_required
def preview(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.user_id is g.user.id and thread.submitted is False:
        return render_template(
            'preview.html',
            thread=thread,
            page_title="Preview and Submit Your AMA"
        )
    elif thread.submitted is True:
        return redirect(url_for(
            'success',
            thread_id=thread.id
        ))
    else:
        abort(404)


@app.route("/edit/<int:thread_id>", methods=['GET', 'POST'])
@login_required
def edit(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.user_id is g.user.id and thread.submitted is False:
        form = ThreadForm(obj=thread)
        if form.validate_on_submit():
            thread.title = form.title.data
            thread.body = form.body.data
            thread.verification = form.verification.data
            thread.subreddit = form.subreddit.data
            db.session.commit()
            return redirect(url_for(
                'preview',
                thread_id=thread.id
            ))
        return render_template(
            'edit.html',
            form=form,
            page_title="Edit Your AMA"
        )
    elif thread.submitted is True:
        return redirect(url_for(
            'success',
            thread_id=thread.id
        ))
    else:
        abort(404)


@app.route("/success/<int:thread_id>")
@login_required
def success(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.user_id is g.user.id:

        if thread.submitted is False:

            # post to reddit
            reddit_post = None

            try:
                r.refresh_access_information(g.user.refresh_token)
                reddit_post = r.submit(
                    thread.subreddit,
                    thread.title,
                    reddit_body(
                        thread.body,
                        thread.verification
                    )
                )

            except praw.errors.APIException as e:
                flash('There was an error with your AMA submission: ' +
                      e.message)

            except praw.errors.ClientException as e:
                flash('There was an error with your AMA submission: ' +
                      e.message)

            except:
                flash('Sorry, we could not create '
                      'your AMA on reddit 2. Try again.')

            if reddit_post:
                thread.submitted = True
                thread.reddit_id = reddit_post.id
                thread.reddit_permalink = reddit_post.permalink
                db.session.commit()
                return render_template(
                    'success.html',
                    thread=thread,
                    page_title="Your AMA has been submitted!"
                )

            else:
                return redirect(url_for(
                    'preview',
                    thread_id=thread.id
                ))

        else:

            return render_template(
                'success.html',
                thread=thread,
                page_title="Your AMA has been submitted!"
            )
    else:
        abort(404)
