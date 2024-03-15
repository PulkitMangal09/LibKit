from flask import Flask
from Applications.database import db

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LibKit.sqlite3'
    db.init_app(app)
    app.app_context().push()

    return app

app = create_app()

from Applications.controller import *  # Models are imported in controller.py and controllers are imported here

if __name__ == '__main__':
    app.run()
