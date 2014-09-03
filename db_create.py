from app import db
from app.models import Role, User, Thread
from datetime import datetime

db.create_all()

db.session.add(
    Role(
        name='Admin'
    )
)
db.session.add(
    Role(
        name='User'
    )
)

db.session.add(
    User(
        username="amapro",
        role_id=1
    )
)

#thread1 = Thread(
#    user_id=1,
#    title=u'Bravely Default - 3DS',
#    category_id=1,
#    reddit_id="1ycqin",
#    reddit_permalink="http://www.reddit.com/r/3DS/comments/1ycqin/i_created_an_app_that_allows_us_to_review_games/",
#    subreddit="3DS",
#    link_url="http://bravelydefault.nintendo.com/",
#    link_text="Official Website for Bravely Default",
#    date_posted=datetime(2014, 2, 19),
#    open_for_comments=False,
#    last_crawl=datetime.now()
#)
#db.session.add(thread1)

db.session.commit()
