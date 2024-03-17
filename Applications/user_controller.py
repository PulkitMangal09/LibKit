from .controller import *
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


#Define the User Daahboard Book View Page
@app.route('/user_dash')
@login_required
def user_dash():
    user=User.query.get(current_user.id)
    books_with_sections = []
    rating=''
    books = Books.query.all()
    for book in books:
        section = Section.query.get(book.bs_id)
        if book.rating:
            rating=book.rating
        else:
            rating='-'
        books_with_sections.append((book, section, rating))
    
        
    
    return render_template('user_dash.html', books_with_sections=books_with_sections, user=user)


#Define the User Dashboard Book Request Behaviour (Borrow Button Behaviour)
@app.route('/<int:id>/request')
@login_required
def request_book(id):

    # Count the number of books with 'accepted' status for the current user
    accepted_books_count = Request.query.filter_by(user_id=current_user.id, status='approved').count()
    
    if accepted_books_count >= 5:
        flash('You have already accepted five books. Please return a book to request another one.')
        return redirect(url_for('user_dash'))


    data=Request.query.all()
    if data:
        for i in data:
            if i.user_id==current_user.id and i.status=='pending' and i.book_id==id:
                flash('You have already requested this book and it is pending approval. Please wait for the admin to approve your request.')
                return redirect(url_for('user_dash'))
            if i.user_id==current_user.id and i.status=='approved'and i.book_id==id:
                flash('You have already requested this book and it is pending return. Please return the book to request another one.')
                return redirect(url_for('user_dash'))
    book = Books.query.get(id)
    user = User.query.get(current_user.id)
    new_request = Request(user_id=user.id, book_id=book.id)
    db.session.add(new_request)
    db.session.commit()
    flash('Your request has been submitted. Please wait for the admin to approve it.')
    return redirect(url_for('user_dash'))


#Define the User Dashboard Book Request Behaviour
        
#Define the Pending Request Page
@app.route('/user_pending_requests')
@login_required
def user_pending_requests():
    data=Request.query.filter_by(status='pending',user_id=current_user.id).all()
    main_data = []
    if len(data)==0:
        return render_template('user_pending_requests.html', error='There are no pending requests at the moment.')
    for i in data:
        book = Books.query.get(i.book_id)
        main_data.append((i, book.title))
    return render_template('user_pending_requests.html', main_data=main_data)


#Define the Approved Request Page
@app.route('/user_approved_requests')
@login_required
def user_approved_requests():
    data=Request.query.filter_by(status='approved',user_id=current_user.id).all()
    main_data = []
    if len(data)==0:
        return render_template('user_approved_requests.html', error='There are no approved books at the moment.')
    for i in data:
        book = Books.query.get(i.book_id)
        main_data.append((book.title, book.author, book.content,book.image,i.id))
    return render_template('user_approved_requests.html', main_data=main_data)



#Define the Return Button Request Page
@app.route('/<int:id>/return_book')
@login_required
def return_book(id):
    data=Request.query.get(id)
    book=Feedback.query.filter_by(book_id=data.book_id,borrow_user_id=current_user.id).first()
    book.phase='returned'
    data.status='return'
    db.session.delete(data)
    db.session.commit()
    flash('The book has been returned.')
    return redirect(url_for('feedback',id=book.book_id))


#Define the Rejected Request Page
@app.route('/user_rejected_requests')
@login_required
def user_rejected_requests():
    data=Request.query.filter_by(status='rejected',user_id=current_user.id).all()
    main_data = []
    if len(data)==0:
        return render_template('user_rejected_requests.html', error='There are no rejected requests at the moment.')
    for i in data:
        book = Books.query.get(i.book_id)
        main_data.append((i, book.title))
    return render_template('user_rejected_requests.html', main_data=main_data)


#Define the stats on User Dashboard

@app.route('/user_general_stats')
@login_required
def user_general_stats():

    import matplotlib
    matplotlib.use('Agg')  # Use Agg backend which doesn't require a GUI
    import matplotlib.pyplot as plt

    # Retrieve the feedback data for the current user
    user_feedback = Feedback.query.filter_by(borrow_user_id=current_user.id).all()

    if len(user_feedback) == 0:
        return render_template('user_general_stats.html', error='You have not borrowed any books yet.')

    # Count the number of books read from each section
    section_counts = {}
    for feedback in user_feedback:
        section_id = feedback.book.section.id
        section_title = feedback.book.section.title
        if section_id in section_counts:
            section_counts[section_id]['count'] += 1
        else:
            section_counts[section_id] = {'title': section_title, 'count': 1}

    # Prepare data for plotting
    section_titles = [section_info['title'] for section_info in section_counts.values()]
    book_counts = [section_info['count'] for section_info in section_counts.values()]



    # Prepare data for pie chart
    labels = [section_info['title'] for section_info in section_counts.values()]
    counts = [section_info['count'] for section_info in section_counts.values()]

    # Create the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Books Read by Section')

    # Convert plot to base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    pie_plot_data = base64.b64encode(buffer.getvalue()).decode()

    # Clear the plot to avoid memory leaks
    plt.clf()

    return render_template('user_general_stats.html', pie_plot_data=pie_plot_data)


##Trying to Calculate the mean feedback##
def calculate_rating(id):
    temp=0
    count=0
    book=Feedback.query.filter_by(book_id=id)
    for i in book:
        if i.feedback:
            temp+=i.feedback
            count+=1
    if count==0:
        return 0
    return round(temp/count,1)
##Trying to Calculate the mean feedback##

#Define the Feedback Page
@app.route('/<int:id>/feedback', methods=['GET', 'POST'])
@login_required
def feedback(id):
    if request.method == 'POST':
        feedback = request.form.get('rating')
        book = Feedback.query.filter_by(book_id=id,borrow_user_id=current_user.id).first()
        book.feedback=feedback
        db.session.commit()
        # Calculate the rating and update the Books table
        book_rating = calculate_rating(id)
        book = Books.query.get(id)
        book.rating = book_rating
        db.session.commit()
        flash('Your feedback has been submitted.')
        return redirect(url_for('user_dash'))
    return render_template('feedback.html', id=id)

