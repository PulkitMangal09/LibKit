from flask import Flask
from Applications.database import db
from Applications.api import api

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LibKit.sqlite3'
    # Set the upload folder configuration
    app.config['UPLOAD_FOLDER'] = 'C:\\Users\\pulki\\OneDrive\\Documents\\MAD 1 Proj\\static\\images'
    db.init_app(app) # Equivalent to write db = SQLAlchemy(app) in database.py
    api.init_app(app) # Equivalent to write api = Api(app) in api.py
    app.app_context().push()

    return app

app = create_app()

from Applications.controller import *  # Models are imported in controller.py and controllers are imported here
from Applications.user_controller import *
from Applications.admin_controller import *

if __name__ == '__main__':
    app.run()
