from flask import render_template, url_for, flash, redirect, request, abort
from backend import app, db, bcrypt
from backend.forms import RegistrationForm, LoginForm, CalendarEventForm, StudyObjectiveForm
from backend.models import User, CalendarEvent, StudyObjective, Achievement
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

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
        try:
            objective = StudyObjective(
                title=form.title.data,
                description=form.description.data,
                target_date=form.target_date.data,
                current_progress=form.current_progress.data,
                user_id=current_user.id
            )
            db.session.add(objective)
            db.session.commit()
            flash('Objective has been added!', 'success')
            return redirect(url_for('objectives'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding objective: {e}', 'danger')
    return render_template('add_objective.html', title='Add Objective', form=form)

@app.route("/achievements")
@login_required
def achievements():
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    return render_template('achievements.html', achievements=achievements)

@app.route("/mark_complete/<int:objective_id>", methods=['POST'])
@login_required
def mark_complete(objective_id):
    objective = StudyObjective.query.get_or_404(objective_id)
    if objective.user_id != current_user.id:
        abort(403)
    objective.completed = 'completed' in request.form
    if objective.completed:
        # Create an achievement entry
        achievement = Achievement(objective_id=objective.id, user_id=current_user.id, date_achieved=datetime.utcnow())
        db.session.add(achievement)
    db.session.commit()
    return redirect(url_for('objectives'))

@app.route("/objective/<int:objective_id>/update", methods=['GET', 'POST'])
@login_required
def update_objective(objective_id):
    objective = StudyObjective.query.get_or_404(objective_id)
    if objective.user_id != current_user.id:
        abort(403)
    form = StudyObjectiveForm()
    if form.validate_on_submit():
        objective.title = form.title.data
        objective.description = form.description.data
        objective.target_date = form.target_date.data
        objective.current_progress = form.current_progress.data
        objective.completed = form.completed.data
        if objective.completed:
            if not Achievement.query.filter_by(objective_id=objective.id).first():
                achievement = Achievement(objective_id=objective.id, user_id=current_user.id, date_achieved=datetime.utcnow())
                db.session.add(achievement)
        else:
            achievement = Achievement.query.filter_by(objective_id=objective.id).first()
            if achievement:
                db.session.delete(achievement)
        db.session.commit()
        flash('Your objective has been updated!', 'success')
        return redirect(url_for('objectives'))
    elif request.method == 'GET':
        form.title.data = objective.title
        form.description.data = objective.description
        form.target_date.data = objective.target_date
        form.current_progress.data = objective.current_progress
        form.completed.data = objective.completed
    return render_template('add_objective.html', title='Update Objective', form=form, legend='Update Objective')

@app.route("/objective/<int:objective_id>/delete", methods=['POST'])
@login_required
def delete_objective(objective_id):
    objective = StudyObjective.query.get_or_404(objective_id)
    if objective.user_id != current_user.id:
        abort(403)
    achievement = Achievement.query.filter_by(objective_id=objective.id).first()
    if achievement:
        db.session.delete(achievement)
    db.session.delete(objective)
    db.session.commit()
    flash('Your objective has been deleted!', 'success')
    return redirect(url_for('objectives'))

@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    form = CalendarEventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.date = form.date.data
        event.description = form.description.data
        db.session.commit()
        flash('Your event has been updated!', 'success')
        return redirect(url_for('calendar'))
    elif request.method == 'GET':
        form.title.data = event.title
        form.date.data = event.date
        form.description.data = event.description
    return render_template('add_event.html', title='Update Event', form=form, legend='Update Event')

@app.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Your event has been deleted!', 'success')
    return redirect(url_for('calendar'))