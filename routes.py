from flask import render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from mxhub import app, db
from mxhub.models import User, Course, Quiz
from mxhub.forms import RegistrationForm, LoginForm


@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)


@app.route('/courses')
def course_list():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@app.route('/quizzes')
def quiz_list():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)


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
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

