from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from . import routes, models