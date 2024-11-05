from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '3c0f4e1f5c4a68832f4957e71fba47c9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    instructor = db.Column(db.String(150), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()  
    if not Course.query.first():  
        sample_courses = [
            Course(title='Python for Beginners', instructor='Maxyn Edogha'),
            Course(title='Data Science with Python', instructor='Peter salvation'),
        ]
        db.session.bulk_save_objects(sample_courses)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html', courses=Course.query.all())

@app.route('/courses')
def course_list():
    return render_template('courses.html', courses=Course.query.all())

@app.route('/quizzes')
def quiz_list():
    return render_template('quizzes.html', quizzes=Quiz.query.all())

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('user_id'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
