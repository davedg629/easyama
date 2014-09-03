from app import app
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup, g
from app.forms import ThreadForm


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ThreadForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'success'
        ))
    return render_template(
        'index.html',
        page_title="Start Your reddit AMA",
        form=form
    )


@app.route("/success")
def success():
    return 'Success!'
