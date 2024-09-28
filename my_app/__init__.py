from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(TestConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from my_app import routes, models
from my_app.dash_pack import create_dash

create_dash(app)