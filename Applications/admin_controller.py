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


# Define the admin dashboard
@app.route('/admin_dash')
@login_required
def admin_dash():

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Section.query.all()
    if len(data)==0:
        return render_template('admin_dash.html', error='Regrettably, we were unable to locate any existing sections. Would you be interested in creating a new section?')
    return render_template('admin_dash.html', data=data)


# Define the add section page
@app.route('/add_section', methods=['GET', 'POST'])
@login_required
def add_section():

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Check if the post request has the file part
        if 'image_file' not in request.files:
            return render_template('add_section.html', error='No file part')
        
        file = request.files['image_file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('add_section.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            # Secure the filename before saving
            filename = secure_filename(file.filename)
            
            # Define the path where the image will be saved
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the uploaded file to the specified path
            file.save(filepath)
        else:
            return render_template('add_section.html', error='Invalid file format')
        
        temp = datetime.datetime.now()
        date = temp.strftime("%B %d, %Y")
        
        existing_section = Section.query.filter_by(title=title).first()
        if existing_section:
            return render_template('add_section.html', error='Section already exists')
        
        # Store only the filename in the database
        new_section = Section(title=title, date=date, image=filename, description=description)
        db.session.add(new_section)
        db.session.commit()
        return redirect(url_for('admin_dash'))
    
    return render_template('add_section.html')


#Define the Preview Page for each Section (On click Section--> Action)
@app.route('/<int:id>/section')
@login_required
def section(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Books.query.filter_by(bs_id=id).all()
    if len(data)==0:
        return render_template('section.html', error="Unfortunately, we couldn't find any books in this section. Would you like to add new books to this section?", id=id)
    return render_template('section.html', data=data,id=id)



# Define the add book page
@app.route('/<int:id>/add_book', methods=['GET', 'POST'])
@login_required
def add_book(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    print("ID:", id) 
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        # Check if the post request has the file part
        if 'image_file' not in request.files:
            return render_template('add_book.html', error='No file part')
        
        file = request.files['image_file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('add_book.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            # Secure the filename before saving
            filename = secure_filename(file.filename)
            
            # Define the path where the image will be saved
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the uploaded file to the specified path
            file.save(filepath)
        else:
            return render_template('add_book.html', error='Invalid file format')
        content= request.form.get('content')
        existing_book = Books.query.filter_by(title=title).first()
        if existing_book:
            return render_template('add_book.html', error='Book already exists')
        new_book = Books(title=title, author=author, image=filename, content=content, bs_id=id)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('section', id=id))
    return render_template('add_book.html', id=id)


# Define the delete section page
@app.route('/<int:id>/delete_section')
@login_required
def delete_section(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Section.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('admin_dash'))

#Define the Update Section Page
@app.route('/<int:id>/update_section', methods=['GET', 'POST'])
@login_required
def update_section(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Section.query.get(id)
    if request.method == 'POST':
        data.title = request.form.get('title')
        date= datetime.datetime.now()
        data.date=date.strftime("%B %d, %Y")
        # Check if the post request has the file part
        if 'image_file' not in request.files:
            return render_template('update_section.html', error='No file part')
        
        file = request.files['image_file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('update_section.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            # Secure the filename before saving
            filename = secure_filename(file.filename)
            
            # Define the path where the image will be saved
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the uploaded file to the specified path
            file.save(filepath)
        else:
            return render_template('update_section.html', error='Invalid file format')
        data.image=filename
        data.description= request.form.get('description')
        db.session.commit()
        return redirect(url_for('admin_dash'))
    return render_template('update_section.html', data=data)


# Define the delete book page
@app.route('/<int:id>/delete_book')
@login_required
def delete_book(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Books.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('section', id=data.bs_id))


#Define the Update Book Page
@app.route('/<int:id>/update_book', methods=['GET', 'POST'])    
@login_required
def update_book(id):

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Books.query.get(id)
    if request.method == 'POST':
        

        data.title = request.form.get('title')
        data.author= request.form.get('author')
        # Check if the post request has the file part
        if 'image_file' not in request.files:
            return render_template('update_book.html', error='No file part')
        
        file = request.files['image_file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('update_book.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            # Secure the filename before saving
            filename = secure_filename(file.filename)
            
            # Define the path where the image will be saved
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the uploaded file to the specified path
            file.save(filepath)
        else:
            return render_template('update_book.html', error='Invalid file format')
        data.image=filename
        data.content= request.form.get('content')
        db.session.commit()
        return redirect(url_for('section', id=data.bs_id))
    return render_template('update_book.html', data=data)






#Define the Admin Dashboard Book Request Behaviour


#Define the Pending Request Page
@app.route('/pending_requests')
@login_required
def pending_requests():
    
    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=Request.query.filter_by(status='pending').all()
    main_data = []
    if len(data)==0:
        return render_template('pending_requests.html', error='There are no pending requests at the moment.')
    for i in data:
        user = User.query.get(i.user_id)
        book = Books.query.get(i.book_id)
        main_data.append((i, user.username, book.title))
    return render_template('pending_requests.html', main_data=main_data)


#Define the Approve Button Request Page
@app.route('/<int:id>/approve_request')
@login_required
def approve_request(id):
    
        #User Authorization
        if current_user.type=='user':
            return render_template('UA.html', error='You are not authorized to view this page') 
        #User Authorization
    
        data=Request.query.get(id)
        user_id = data.user_id
    
        # Check if the user has already accepted five books
        accepted_books_count = Request.query.filter_by(user_id=user_id, status='approved').count()
        if accepted_books_count >= 5:
            flash('User has already accepted five books. Cannot approve new request.')
            return redirect(url_for('pending_requests'))


        book=Books.query.get(data.book_id)
        new_feedback = Feedback(borrow_user_id=user_id, book_id=book.id)
        db.session.add(new_feedback)
        data.status='approved'
        db.session.commit()
        flash('The request has been approved. The user can now read the book.')
        return redirect(url_for('pending_requests'))


#Define the Reject Button Request Page
@app.route('/<int:id>/reject_request')
@login_required
def reject_request(id):
        
            #User Authorization
            if current_user.type=='user':
                return render_template('UA.html', error='You are not authorized to view this page') 
            #User Authorization
        
            data=Request.query.get(id)
            data.status='rejected'
            db.session.commit()
            flash('The request has been rejected. The user cannot borrow the book.')
            return redirect(url_for('pending_requests'))


#Define the approved Request Page
@app.route('/approved_requests')
@login_required
def approved_requests():
        
        #User Authorization
        if current_user.type=='user':
            return render_template('UA.html', error='You are not authorized to view this page') 
        #User Authorization
    
        data=Request.query.filter_by(status='approved').all()
        main_data = []
        if len(data)==0:
            return render_template('approved_requests.html', error='There are no approved requests at the moment.')
        for i in data:
            user = User.query.get(i.user_id)
            book = Books.query.get(i.book_id)
            main_data.append((i, user.username, book.title))
        return render_template('approved_requests.html', main_data=main_data)


#Define the Revoke Button Request Page
@app.route('/<int:id>/revoke_request')
@login_required
def revoke_request(id):
                
                #User Authorization
                if current_user.type=='user':
                    return render_template('UA.html', error='You are not authorized to view this page') 
                #User Authorization
            
                data=Request.query.get(id)
                book=Feedback.query.get(data.book_id)
                book.phase='returned'
                data.status='revoked'
                db.session.delete(data)
                db.session.commit()
                flash('The request has been revoked. The user cannot see the book.')
                return redirect(url_for('approved_requests'))


#Define the Rejected Request Page
@app.route('/rejected_requests')
@login_required
def rejected_requests():
        #User Authorization
        if current_user.type=='user':
            return render_template('UA.html', error='You are not authorized to view this page') 
        #User Authorization
                    
        data=Request.query.filter_by(status='rejected').all()
        main_data = []
        if len(data)==0:
            return render_template('rejected_requests.html', error='There are no rejected requests at the moment.')
        for i in data:
            user = User.query.get(i.user_id)
            book = Books.query.get(i.book_id)
            main_data.append((i, user.username, book.title))
        return render_template('rejected_requests.html', main_data=main_data)
        

#Define the User Stats on Admin Dashboard

@app.route('/user_stats')
@login_required
def user_stats():
    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=User.query.all()
    if len(data)==0:
        return render_template('user_stats.html', error='There are no users at the moment.')
    return render_template('user_stats.html', data=data)


#Define the User Info on Admin Dashboard while clicking user button on User Stas Page
@app.route('/<int:id>/user_info')
@login_required
def user_info(id):

    import matplotlib
    matplotlib.use('Agg')  # Use Agg backend which doesn't require a GUI
    import matplotlib.pyplot as plt
    

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    data=User.query.filter_by(id=id)
    books = Books.query.all()
    user_books=Feedback.query.filter_by(borrow_user_id=id).all()
    # print(len(books),len(user_books))


    borrowed_books = len(user_books)
    total_books = len(books)
    # Calculate the ratio of borrowed books to total books
    borrowed_ratio = borrowed_books / total_books
    remaining_ratio = 1 - borrowed_ratio

    # Create a pie chart
    labels = ['Borrowed Books', 'Remaining Books']
    sizes = [borrowed_ratio, remaining_ratio]
    colors = ['lightcoral', 'lightskyblue']

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Ratio of Borrowed Books to Total Books')

    # Convert the plot to a base64 encoded string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()

    plt.close()

    return render_template('user_info.html', data=data, chart_data=chart_data)



#Define the general stats on Admin Dashboard
@app.route('/general_stats')
@login_required
def general_stats():

    import matplotlib
    matplotlib.use('Agg')  # Use Agg backend which doesn't require a GUI
    import matplotlib.pyplot as plt
    

    #User Authorization
    if current_user.type=='user':
        return render_template('UA.html', error='You are not authorized to view this page') 
    #User Authorization

    # Query database to get the number of books in each section
    sections = Section.query.all()
    section_titles = [section.title for section in sections]
    book_counts = [len(section.books) for section in sections]

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(section_titles, book_counts, color='skyblue')
    plt.xlabel('Section')
    plt.ylabel('Number of Books')
    plt.title('Number of Books in Each Section')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Convert plot to base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    # Clear the plot to avoid memory leaks
    plt.clf()

    return render_template('admin_stats.html', plot_data=plot_data)


#Define the issued users page on Admin Dashboard
@app.route('/<int:id>/issued_users')
@login_required
def issued_users(id):
        
        #User Authorization
        if current_user.type=='user':
            return render_template('UA.html', error='You are not authorized to view this page') 
        #User Authorization
    
        data=Feedback.query.filter_by(book_id=id).all()
        if len(data)==0:
            return render_template('issued_users.html', error='There are no issued users at the moment.')

        section_id=Books.query.get(id).bs_id

        main_data=[]

        for i in data:
            user = User.query.filter_by(id=i.borrow_user_id).first()
            main_data.append((user.username, user.name,user.email))

        return render_template('issued_users.html', main_data=main_data,section_id=section_id)
