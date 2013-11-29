from flask import Flask

# For SqlAlchemy
#from flask.ext.sqlalchemy import SQLAlchemy

import config
import routes

from params import PI_BASE_URL

app = Flask("sample-project", static_folder='media', static_url_path=PI_BASE_URL+'media')
# For SqlAlchemy
#app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL
#db = SQLAlchemy(app)

def load_actions(act_mod):
    routes.load_routes(app, act_mod)
