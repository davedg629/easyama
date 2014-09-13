from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup, g
from app.forms import ThreadForm
from app.models import Thread


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
