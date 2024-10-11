import random

from my_app import app, db
from my_app.models import MaterialType


with app.app_context():
    types = MaterialType.query.all()
    for i in types:
        if i.name == 'Стали' or i.name == 'jkljlk':
            db.session.delete(i)

    db.session.commit()