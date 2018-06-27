from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegisterForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, load_user
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Clay'}
    return render_template('index.html', user = user, title='Home Page')

@app.route('/posts', methods = ['GET', 'POST'])
@login_required
def posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('posts'))

    if current_user.is_authenticated:
        posts = current_user.posts
    else:
        posts = []
    return render_template('posts.html', title='Posts', form=form, posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('index')
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid login credentials')
            return redirect(url_for('login'))
        login_user(user, remember = login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash('Thanks for logging in {}'.format(current_user.username))
        return redirect(url_for('login'))
    return render_template('login.html', form=login_form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('index')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.useremail.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect('login')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
