from .database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), default='user')
    requests = db.relationship('Request', backref='user')
    feedbacks = db.relationship('Feedback', backref='borrowed_feedbacks')

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    books = db.relationship('Books', backref='section', cascade='all, delete')

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    content= db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(80), nullable=True)
    bs_id = db.Column(db.Integer(), db.ForeignKey('section.id'), nullable=False)
    rating = db.Column(db.Float(200),default=0.0)
    book_requests = db.relationship('Request', backref='books', cascade='all, delete')
    feedbacks = db.relationship('Feedback', backref='book', cascade='all, delete')
    

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'), nullable=False)
    status = db.Column(db.String(80), nullable=False,default='pending')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrow_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    feedback = db.Column(db.Integer())
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'), nullable=False)
    phase= db.Column(db.String(80), default='currently borrowing')
    
    