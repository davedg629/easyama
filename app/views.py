from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, g
from app.forms import ThreadForm, DeleteThreadForm, CaptchaForm
from app.models import Thread, User
from flask.ext.login import login_user, logout_user, \
    login_required, current_user
from app.utils import generate_token, reddit_body
from sqlalchemy import desc
import praw


@app.before_request
def before_request():
    if current_user.is_authenticated():
        g.user = current_user
    else:
        g.user = None


# ERROR HANDLERS
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template(
        '404.html',
        title="Page Not Found",
        page_title="Page Not Found"
    ), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template(
        '500.html',
        title="Error",
        page_title="Error!"
    ), 500


# REDDIT LOGIN
@app.route('/authorize/')
def authorize():
    state = request.args.get('state', '')
    if current_user.is_anonymous() and (state == session['oauth_token']):
        try:
            code = request.args.get('code', '')
            r = praw.Reddit(user_agent=app.config['REDDIT_USER_AGENT'])
            r.set_oauth_app_info(
                app.config['REDDIT_APP_ID'],
                app.config['REDDIT_APP_SECRET'],
                app.config['OAUTH_REDIRECT_URI']
            )
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
            return redirect(url_for('login'))
        except praw.errors.OAuthException:
            flash('There was a problem with your login. Please try again.')
            return redirect(url_for('login'))
        except:
            flash('Sorry, there was an error. Please try again later.')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


# logout
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# how it works
@app.route("/how-it-works")
def how_it_works():
    return render_template(
        'how-it-works.html',
        page_title="How It Works"
    )


# homepage
@app.route("/")
def index():
    return render_template(
        'index.html',
        page_title="Ready to create an AMA? Read this first."
    )


# login page
@app.route("/login")
def login():
    if current_user.is_authenticated():
        saved_threads = db.session.query(Thread)\
            .filter_by(user_id=g.user.id)\
            .filter_by(submitted=False)\
            .first()
        if saved_threads:
            return redirect(url_for('user'))
        else:
            return redirect(url_for('create_thread'))
    r = praw.Reddit(user_agent=app.config['REDDIT_USER_AGENT'])
    r.set_oauth_app_info(
        app.config['REDDIT_APP_ID'],
        app.config['REDDIT_APP_SECRET'],
        app.config['OAUTH_REDIRECT_URI']
    )
    session['oauth_token'] = generate_token()
    oauth_link = r.get_authorize_url(
        session['oauth_token'],
        ['identity', 'submit'],
        True
    )
    return render_template(
        'login.html',
        page_title="Step 1: Login with your reddit account",
        oauth_link=oauth_link
    )


# create thread
@app.route("/create/", methods=['GET', 'POST'])
@login_required
def create_thread():
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
        'create-thread.html',
        page_title="Step 2: Create your reddit AMA",
        form=form
    )


# preview thread
@app.route("/preview/<int:thread_id>")
@login_required
def preview(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if ((thread and thread.user_id is g.user.id) or (g.user.role_id is 1)) \
            and thread.submitted is False:
        return render_template(
            'preview.html',
            thread=thread,
            page_title="Step 3: Preview and Submit Your AMA"
        )
    elif thread.submitted is True:
        return redirect(url_for(
            'success',
            thread_id=thread.id
        ))
    else:
        abort(404)


# share thread
@app.route("/share/<int:thread_id>")
def share(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.submitted is False:
        return render_template(
            'share.html',
            thread=thread,
            page_title="AMA Preview"
        )
    else:
        abort(404)


# edit thread
@app.route("/edit/<int:thread_id>", methods=['GET', 'POST'])
@login_required
def edit(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if ((thread and thread.user_id is g.user.id) or (g.user.role_id is 1)) \
            and thread.submitted is False:
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


# submit thread/success
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
                r = praw.Reddit(user_agent=app.config['REDDIT_USER_AGENT'])
                r.set_oauth_app_info(
                    app.config['REDDIT_APP_ID'],
                    app.config['REDDIT_APP_SECRET'],
                    app.config['OAUTH_REDIRECT_URI']
                )
                r.refresh_access_information(g.user.refresh_token)
                if request.args.get('captcha_id', '') \
                        and request.args.get('captcha_response', ''):
                    captcha = {
                        'iden': request.args.get('captcha_id', ''),
                        'captcha': request.args.get('captcha_response', '')
                    }
                    reddit_post = r.submit(
                        thread.subreddit,
                        thread.title,
                        reddit_body(
                            thread.body,
                            thread.verification
                        ),
                        captcha=captcha,
                        raise_captcha_exception=True
                    )
                else:
                    reddit_post = r.submit(
                        thread.subreddit,
                        thread.title,
                        reddit_body(
                            thread.body,
                            thread.verification
                        ),
                        raise_captcha_exception=True
                    )

            except praw.errors.InvalidCaptcha as e:
                return redirect(url_for(
                    'captcha',
                    thread_id=thread.id,
                    captcha_id=e.response['captcha']
                ))
            except praw.errors.APIException as e:
                flash('There was an error with your AMA submission: ' +
                      str(e.message))

            except praw.errors.ClientException as e:
                flash('There was an error with your AMA submission: ' +
                      str(e.message))

            except:
                flash('Sorry, we could not create '
                      'your AMA on reddit. Please try again.')

            if reddit_post is not None:
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


# captcha form
@app.route('/captcha/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def captcha(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.user_id is g.user.id and thread.submitted is False:
        form = CaptchaForm()
        if form.validate_on_submit():
            return redirect(url_for(
                'success',
                thread_id=thread.id,
                captcha_id=request.args.get('captcha_id', ''),
                captcha_response=form.captcha_response.data
            ))
        return render_template(
            'captcha.html',
            form=form,
            captcha=request.args.get('captcha_id', '')
        )
    else:
        abort(404)


# list threads
@app.route('/latest/', defaults={'pagenum': 1})
@app.route("/latest/<int:pagenum>")
def latest_threads(pagenum):
    threads = Thread.query\
        .filter_by(submitted=True)\
        .paginate(pagenum, 10, False)
    return render_template(
        'latest-threads.html',
        threads=threads,
        page_title="Latest AMA's made with easyAMA"
    )


# delete thread
@app.route('/delete/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def delete_thread(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread and thread.user.id == g.user.id:
        form = DeleteThreadForm()
        if form.validate_on_submit():
            db.session.delete(thread)
            db.session.commit()
            flash("Your AMA has been deleted.")
            return redirect(url_for(
                'user',
            ))
        else:
            return render_template(
                'delete-thread.html',
                thread=thread,
                form=form,
                page_title="Delete AMA"
            )
    else:
        return abort(404)


# user profile
@app.route('/user/')
@login_required
def user():
    if current_user.is_authenticated():
        threads_not_submitted = db.session.query(Thread)\
            .filter_by(user_id=g.user.id)\
            .filter_by(submitted=False)\
            .order_by(desc(Thread.date_posted))\
            .all()
        threads_submitted = db.session.query(Thread)\
            .filter_by(user_id=g.user.id)\
            .filter_by(submitted=True)\
            .order_by(desc(Thread.date_posted))\
            .all()
        return render_template(
            'user.html',
            user=g.user,
            threads_not_submitted=threads_not_submitted,
            threads_submitted=threads_submitted,
            page_title="My Account"
        )
    else:
        return abort(404)
