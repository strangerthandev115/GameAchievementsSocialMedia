from flask import render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash #Module to hash passwords

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Example user storage (you'd likely use a database)
users = {
    "user1": {"password": "password123"},
}

# User class required by Flask-Login
'''class User(UserMixin):
    def __init__(self, username):
        self.id = username'''

# Load user function for Flask-Login
'''@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None'''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('registration.html')

@app.route('/profile')
@login_required  # Protect this route, user must be logged in
def profile():
    return render_template('profile.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', show_navbar=True)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/games')
@login_required
def games():
    return render_template('games.html')

@app.route('/search')
@login_required
def search():
    return render_template('searchresults.html', show_navbar=True)

@app.route('/registration')
def registration():
    return render_template('registration.html')


#Login logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists and the password matches
        user = User.query.filter_by(Username=username).first()  # Search for the user by username
        
        if user and check_password_hash(user.Password, password):  # Check if username exists and password matches
            login_user(user)  # Log the user in using Flask-Login
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard

        else:
            flash('Invalid username or password', 'danger')  # Show error message if login fails

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


#Registration logic
@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rpassword = request.form['rpassword']

        # Validate the input
        if password != rpassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register')) #Refresh registration page if passwords do not match

        # Check if the username already exists
        existing_user = db.session.query(User).filter_by(Username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('register')) #Refresh registration page if username already in use

        #Hashing password before storing in db
        hashed_password = generate_password_hash(password)

        # Create a new user without hashing the password
        new_user = User(Username=username, Password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('registration.html')