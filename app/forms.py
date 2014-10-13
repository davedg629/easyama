from flask_wtf import Form
from wtforms import TextField, SubmitField
from wtforms.validators import InputRequired, Length, URL
from flask.ext.pagedown.fields import PageDownField


# frontend thread creation form
class ThreadForm(Form):

    subreddit = TextField('Subreddit', validators=[InputRequired()])

    title = TextField(
        'Title',
        validators=[
            InputRequired(),
            Length(
                max=300,
                message="Title cannot be longer than 300 characters"
            )
        ]
    )

    body = PageDownField(
        'Body',
        validators=[
            InputRequired(),
            Length(
                max=2500,
                message="Description cannot be longer than 2500 characters"
            )
        ]
    )

    verification = TextField(
        'Verification Link',
        validators=[
            InputRequired(),
            URL(require_tld=True)
        ]
    )

    submit = SubmitField('Preview')
