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

        