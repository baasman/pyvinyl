from app import *
from user_management import LoginForm, RegistrationForm, User

from flask import request, redirect, render_template, flash, url_for
from flask_login import login_user, logout_user

import sys


@login_manager.user_loader
def load_user(user):
    user = mongo.db.users.find_one({'user': user})
    if user:
        return User(username=user['user'])
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST': # and form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        if user and User.validate_login(user['password_hash'], form.password.data):
            user_obj = User(user['user'])
            login_user(user_obj)
            flash('Logged in successfully. Happy scrobbling', category='success')
            return redirect(url_for('collection', username=user['user']))
        else:
            flash('No email found')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if request.method == 'POST' and reg_form.validate_on_submit():
        user_obj = User(email=reg_form.email.data,
                        username=reg_form.username.data,
                        discogs_user=reg_form.discogs_user.data,
                        unhashed_password=reg_form.password.data)
        user_obj.set_password(reg_form.password.data)
        try:
            n = mongo.db.users.insert_one({'user': user_obj.username,
                                          'email': user_obj.email,
                                          'password_hash': user_obj.password_hash,
                                           'discogs_user': user_obj.discogs_user,
                                           'records': []})
            login_user(user_obj)
            flash('Thanks for registering')
            return redirect(url_for('collection', username=user_obj.username))
        except:
            print(sys.exc_info()[:2])
    return render_template('register.html', form=reg_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('collection', username='logged out check'))


@app.route('/collection/<username>')
def collection(username):
    return render_template('collection.html', username=username)


@app.route('/')
def home():
    return render_template('home.html')