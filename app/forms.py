from flask_wtf import Form
from wtforms import TextField, SubmitField,\
    TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length


# frontend thread creation form
class ThreadForm(Form):

    subreddit = TextField('Choose a Subreddit:', validators=[InputRequired()])

    title = TextField(
        'Enter a title for your reddit AMA:',
        validators=[
            InputRequired(),
            Length(
                max=300,
                message="Title cannot be longer than 300 characters"
            )
        ]
    )

    body = TextAreaField(
        'Provide details about who you are and why you are doing this AMA:',
        validators=[
            InputRequired(),
            Length(
                max=600,
                message="Description cannot be longer than 600 characters"
            )
        ]
    )

    verification = TextField(
        'Provide a link that verifies your identity:',
        validators=[
            InputRequired()
        ]
    )

    test_mode = BooleanField('Test mode?')
    submit = SubmitField()
