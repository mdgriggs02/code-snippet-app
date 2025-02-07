from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Snippet
from app import db

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/')
@main.route('/snippets')
@login_required
def snippets():
    search = request.args.get('search', '')
    tag = request.args.get('tag', '')
    
    query = Snippet.query.filter_by(user_id=current_user.id)
    
    if search:
        query = query.filter(
            (Snippet.title.contains(search)) |
            (Snippet.description.contains(search)) |
            (Snippet.tags.contains(search))
        )
    if tag:
        query = query.filter(Snippet.tags.contains(tag))
        
    snippets = query.order_by(Snippet.timestamp.desc()).all()
    return render_template('snippets.html', snippets=snippets)

@main.route('/add_snippet', methods=['GET', 'POST'])
@login_required
def add_snippet():
    if request.method == 'POST':
        snippet = Snippet(
            title=request.form['title'],
            code=request.form['code'],
            language=request.form['language'],
            description=request.form['description'],
            tags=request.form['tags'],
            user_id=current_user.id
        )
        db.session.add(snippet)
        db.session.commit()
        flash('Snippet added successfully!')
        return redirect(url_for('main.snippets'))
    return render_template('add_snippet.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('main.snippets'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 