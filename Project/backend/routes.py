from flask import render_template, url_for, flash, redirect, request
from backend import app, db, bcrypt
from backend.forms import RegistrationForm, LoginForm, CalendarEventForm, StudyObjectiveForm
from backend.models import User, CalendarEvent, StudyObjective, Achievement
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/calendar")
@login_required
def calendar():
    events = CalendarEvent.query.filter_by(user_id=current_user.id).all()
    return render_template('calendar.html', events=events)

@app.route("/add_event", methods=['GET', 'POST'])
@login_required
def add_event():
    form = CalendarEventForm()
    if form.validate_on_submit():
        event = CalendarEvent(title=form.title.data, date=form.date.data, description=form.description.data, user_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash('Event has been added to your calendar!', 'success')
        return redirect(url_for('calendar'))
    return render_template('add_event.html', title='Add Event', form=form)

@app.route("/objectives")
@login_required
def objectives():
    objectives = StudyObjective.query.filter_by(user_id=current_user.id).all()
    return render_template('objectives.html', objectives=objectives)

@app.route("/add_objective", methods=['GET', 'POST'])
@login_required
def add_objective():
    form = StudyObjectiveForm()
    if form.validate_on_submit():
        objective = StudyObjective(title=form.title.data, description=form.description.data, target_date=form.target_date.data, current_progress=form.current_progress.data, user_id=current_user.id)
        db.session.add(objective)
        db.session.commit()
        flash('Objective has been added!', 'success')
        return redirect(url_for('objectives'))
    return render_template('add_objective.html', title='Add Objective', form=form)

@app.route("/achievements")
@login_required
def achievements():
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    return render_template('achievements.html', achievements=achievements)