from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app as app
from .models import *
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
from io import BytesIO
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os
import base64
import datetime
import numpy as np


#Define the Login Manager
login_manager = LoginManager(app)   

app.config['SECRET_KEY'] = 'myverysecretkey'    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# Custom error handler for 401 Unauthorized
@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('UA.html', error='You are not authorized to view this page') , 401



# Define the allowed extensions for image files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the filename has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# Define the home page
@app.route('/')
def index():
    return render_template('index.html')


# Define the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('password')    
        this_user=User.query.filter_by(username=uname).first()
        if this_user:
            if check_password_hash(this_user.password, password):
                if this_user.type=='admin':
                    login_user(this_user)    #Admin Authorization
                    return redirect(url_for('admin_dash'))
                else:
                    login_user(this_user)   #User Authorization
                    return redirect(url_for('user_dash'))
            else:
                return render_template('login.html', error='Invalid Password')
        else:
            return render_template('login.html', error='Invalid Username, Username Does Not Exist')
        
    return render_template('login.html')


# Define the register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        hashed_password = generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')




#Define the Search Functionality
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search = request.form.get('search')
        books = Books.query.join(Section, Books.bs_id == Section.id).filter(or_(

            Books.title.like(f'%{search}%'),
            Books.author.like(f'%{search}%'),
            Section.title.like(f'%{search}%')
            
        )).all()
        
        if len(books)==0:
            return render_template('search.html', error='No books found with the given search term.',search=search)
        if current_user.type=='admin':
            return render_template('admin_search.html', books=books,search=search)
        return render_template('search.html', books=books,search=search)
    return render_template('search.html')

        