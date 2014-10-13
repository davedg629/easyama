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
        username="letgoandflow",
        role_id=1
    )
)

db.session.commit()
